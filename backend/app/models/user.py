from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db

ROLES = ("admin", "agent", "customer")


class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(190), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(*ROLES, name="user_role"), nullable=False, default="customer", index=True)
    account_status = db.Column(db.Enum("active", "inactive", name="account_status"), nullable=False, default="active")
    profile_photo = db.Column(db.String(255), nullable=True)
    is_seed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.account_status == "active"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "profile_photo": self.profile_photo,
            "account_status": self.account_status,
            "is_seed": self.is_seed,
            "created_at": self.created_at.isoformat() + "Z",
        }

    def brief(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "profile_photo": self.profile_photo,
        }


class TokenBlocklist(db.Model):
    """Revoked JWT ids (logout)."""
    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)


class PasswordResetToken(db.Model):
    """Password reset tokens sent to email."""
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    token = db.Column(db.String(100), nullable=False, unique=True, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User")


class AppSetting(db.Model):
    """Key/value application settings (SLA targets, auto-close days...)."""
    __tablename__ = "app_settings"
    key = db.Column(db.String(80), primary_key=True)
    value = db.Column(db.String(255), nullable=False)
