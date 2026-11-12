import secrets
from datetime import datetime, timedelta

from ..extensions import db
from ..models import PasswordResetToken, User
from ..utils.error_handlers import ApiError
from ..utils.security import create_token
from ..utils.validators import raise_if, validate_email, validate_password
from . import audit_service, email_service


def register_user(name, email, password, role="customer", is_seed=False):
    errors = {}
    email = (email or "").strip().lower()
    if not name or len(name.strip()) < 2:
        errors["name"] = "Name must be at least 2 characters."
    if not validate_email(email):
        errors["email"] = "A valid email is required."
    pw_err = validate_password(password)
    if pw_err:
        errors["password"] = pw_err
    raise_if(errors)
    if User.query.filter_by(email=email).first():
        raise ApiError("An account with this email already exists.", 409, "duplicate_email", {"email": "Email already registered."})
    user = User(name=name.strip(), email=email, role=role, is_seed=is_seed)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def login(email, password):
    user = User.query.filter_by(email=(email or "").strip().lower()).first()
    if not user or not user.check_password(password or ""):
        raise ApiError("Invalid email or password.", 401, "invalid_credentials")
    if not user.is_active:
        raise ApiError("Your account has been deactivated. Contact an administrator.", 403, "account_inactive")
    token, exp = create_token(user)
    audit_service.audit(user, "login", "user", user.user_id, "User logged in")
    db.session.commit()
    return user, token, exp


def request_password_reset(email):
    """Generate a secure password reset token and send an email to the user."""
    email = (email or "").strip().lower()
    if not email:
        return True  # Avoid email enumeration timing leaks
    user = User.query.filter_by(email=email).first()
    if not user or not user.is_active:
        return True  # Never disclose whether account exists

    # Invalidate prior unused tokens
    PasswordResetToken.query.filter_by(user_id=user.user_id, used=False).update({"used": True})
    token_str = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)
    prt = PasswordResetToken(user_id=user.user_id, token=token_str, expires_at=expires, used=False)
    db.session.add(prt)
    db.session.commit()

    reset_link = f"http://localhost:5173/reset-password?token={token_str}"
    body = (
        f"Hello {user.name},\n\n"
        f"We received a request to reset your password for your Helpdesk account.\n"
        f"You can reset your password by clicking the link below (valid for 1 hour):\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email and your password will remain unchanged."
    )
    html_body = email_service.render_email_template(
        title="Password Reset Request",
        headline="Reset Your Account Password",
        paragraphs=[
            f"Hello {user.name},",
            "We received a request to reset the password for your Helpdesk account.",
            "Click the button below to choose a new password. This reset link is valid for 1 hour.",
            "If you did not make this request, you can safely ignore this email; your account remains secure."
        ],
        cta_text="Reset Password",
        cta_url=reset_link
    )
    email_service.send_email(user.email, "[Helpdesk] Password Reset Request", body, html_body=html_body)
    audit_service.audit(user, "password_reset_requested", "user", user.user_id, "Reset token generated")
    return True


def reset_password_with_token(token_str, new_password):
    """Verify reset token and update user password."""
    errors = {}
    pw_err = validate_password(new_password)
    if pw_err:
        errors["password"] = pw_err
    raise_if(errors)

    prt = PasswordResetToken.query.filter_by(token=token_str, used=False).first()
    if not prt:
        raise ApiError("This password reset link is invalid or has already been used.", 400, "invalid_token")
    if prt.expires_at < datetime.utcnow():
        raise ApiError("This password reset link has expired. Please request a new one.", 400, "expired_token")

    user = prt.user
    if not user or not user.is_active:
        raise ApiError("Account not found or inactive.", 404, "user_not_found")

    user.set_password(new_password)
    prt.used = True
    audit_service.audit(user, "password_reset_completed", "user", user.user_id, "Password reset via token")
    db.session.commit()
    return True
