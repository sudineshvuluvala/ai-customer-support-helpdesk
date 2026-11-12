import re

from flask import request

from .error_handlers import ApiError

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")


def json_body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object.", 400, "invalid_json")
    return data


def get_str(data, key, required=True, max_len=255, min_len=1, errors=None):
    val = data.get(key)
    if val is None or (isinstance(val, str) and not val.strip()):
        if required:
            (errors if errors is not None else {}).update({key: "This field is required."})
            if errors is None:
                raise ApiError("Validation failed.", 422, "validation_error", {key: "This field is required."})
        return None
    if not isinstance(val, str):
        if errors is not None:
            errors[key] = "Must be text."
            return None
        raise ApiError("Validation failed.", 422, "validation_error", {key: "Must be text."})
    val = val.strip()
    if len(val) < min_len or len(val) > max_len:
        msg = f"Must be between {min_len} and {max_len} characters."
        if errors is not None:
            errors[key] = msg
            return None
        raise ApiError("Validation failed.", 422, "validation_error", {key: msg})
    return val


def validate_email(email):
    return bool(email and EMAIL_RE.match(email) and len(email) <= 190)


def validate_password(pw):
    if not isinstance(pw, str) or len(pw) < 8 or len(pw) > 128:
        return "Password must be 8-128 characters."
    if not (re.search(r"[A-Za-z]", pw) and re.search(r"\d", pw)):
        return "Password must contain letters and digits."
    return None


def raise_if(errors):
    if errors:
        raise ApiError("Validation failed.", 422, "validation_error", errors)


def page_params(default_per_page=10, max_per_page=100):
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", default_per_page)), 1), max_per_page)
    except ValueError:
        raise ApiError("page and per_page must be integers.", 400, "bad_request")
    return page, per_page


def like_escape(term):
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
