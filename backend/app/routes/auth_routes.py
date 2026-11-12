from datetime import datetime

from flask import Blueprint, g, request

from ..extensions import db, limiter
from ..models import TokenBlocklist
from ..services import audit_service, auth_service, notification_service as ns
from ..utils.error_handlers import ApiError, ok
from ..utils.permissions import current_user, login_required
from ..utils.validators import get_str, json_body

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@bp.post("/register")
@limiter.limit("10 per hour")
def register():
    d = json_body()
    user = auth_service.register_user(d.get("name"), d.get("email"), d.get("password"), role="customer")
    audit_service.audit(user, "register", "user", user.user_id, "Customer registered")
    db.session.commit()
    return ok(user.to_dict(), "Registration successful. You can now log in.", 201)


@bp.post("/login")
@limiter.limit("20 per minute")
def login():
    d = json_body()
    user, token, exp = auth_service.login(d.get("email"), d.get("password"))
    return ok({"token": token, "expires_at": exp.isoformat() + "Z", "user": user.to_dict()}, "Login successful.")


@bp.post("/logout")
@login_required
def logout():
    p = g.token_payload
    db.session.add(TokenBlocklist(jti=p["jti"], expires_at=datetime.utcfromtimestamp(p["exp"])))
    audit_service.audit(current_user(), "logout", "user", current_user().user_id, "User logged out")
    # purge expired blocklist rows opportunistically
    TokenBlocklist.query.filter(TokenBlocklist.expires_at < datetime.utcnow()).delete()
    db.session.commit()
    return ok(None, "Logged out.")


@bp.get("/me")
@login_required
def me():
    u = current_user()
    return ok({**u.to_dict(), "unread_notifications": ns.unread_count(u)})


@bp.post("/forgot-password")
@limiter.limit("5 per minute")
def forgot_password():
    d = json_body()
    email = d.get("email")
    auth_service.request_password_reset(email)
    return ok(None, "If an account matches that email, a password reset link has been sent.")


@bp.post("/reset-password")
@limiter.limit("10 per hour")
def reset_password():
    d = json_body()
    token = d.get("token")
    new_password = d.get("password")
    if not token:
        raise ApiError("Reset token is required.", 400, "token_missing")
    auth_service.reset_password_with_token(token, new_password)
    return ok(None, "Your password has been reset successfully. You can now log in.")
