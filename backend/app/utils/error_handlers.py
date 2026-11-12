import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

log = logging.getLogger(__name__)


class ApiError(Exception):
    def __init__(self, message, status=400, code="bad_request", details=None):
        super().__init__(message)
        self.message, self.status, self.code, self.details = message, status, code, details


def ok(data=None, message=None, status=200, **extra):
    body = {"success": True, "data": data}
    if message:
        body["message"] = message
    body.update(extra)
    return jsonify(body), status


def paginated(items, page, per_page, total, **extra):
    pages = (total + per_page - 1) // per_page if per_page else 1
    return ok(items, pagination={"page": page, "per_page": per_page, "total": total, "pages": pages}, **extra)


def error_response(message, status, code, details=None):
    body = {"success": False, "error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return jsonify(body), status


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _api(e):
        return error_response(e.message, e.status, e.code, e.details)

    @app.errorhandler(HTTPException)
    def _http(e):
        codes = {404: "not_found", 405: "method_not_allowed", 413: "file_too_large", 429: "rate_limited"}
        msg = {413: "Uploaded file is too large.", 429: "Too many requests. Please slow down."}.get(e.code, e.description)
        return error_response(msg, e.code, codes.get(e.code, "http_error"))

    @app.errorhandler(Exception)
    def _unhandled(e):
        from ..extensions import db
        db.session.rollback()
        log.exception("Unhandled error")
        return error_response("An unexpected server error occurred.", 500, "server_error")
