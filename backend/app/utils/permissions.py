from functools import wraps

import jwt
from flask import g, request

from ..extensions import db
from ..models import TokenBlocklist, User
from .error_handlers import ApiError
from .security import decode_token


def _authenticate():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise ApiError("Authentication required.", 401, "unauthorized")
    try:
        payload = decode_token(header[7:])
    except jwt.ExpiredSignatureError:
        raise ApiError("Session expired. Please log in again.", 401, "token_expired")
    except jwt.InvalidTokenError:
        raise ApiError("Invalid authentication token.", 401, "invalid_token")
    if db.session.query(TokenBlocklist.id).filter_by(jti=payload["jti"]).first():
        raise ApiError("Session has been logged out.", 401, "token_revoked")
    user = db.session.get(User, int(payload["sub"]))
    if not user:
        raise ApiError("User not found.", 401, "unauthorized")
    if not user.is_active:
        raise ApiError("Your account has been deactivated.", 403, "account_inactive")
    g.current_user, g.token_payload = user, payload
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        _authenticate()
        return fn(*a, **kw)
    return wrapper


def roles_required(*roles):
    """Backend role-based authorization decorator."""
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            user = _authenticate()
            if user.role not in roles:
                raise ApiError("You do not have permission to perform this action.", 403, "forbidden")
            return fn(*a, **kw)
        return wrapper
    return deco


def current_user():
    return g.current_user
