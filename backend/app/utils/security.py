import uuid
from datetime import datetime, timedelta

import jwt
from flask import current_app


def create_token(user):
    now = datetime.utcnow()
    exp = now + timedelta(minutes=current_app.config["JWT_EXPIRY_MINUTES"])
    payload = {"sub": str(user.user_id), "role": user.role, "jti": uuid.uuid4().hex, "iat": now, "exp": exp}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256"), exp


def decode_token(token):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
