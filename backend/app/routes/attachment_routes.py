from flask import Blueprint, current_app, request, send_file

from ..extensions import db
from ..models import TicketAttachment
from ..services import attachment_service as ats, ticket_service as ts
from ..utils import file_helpers as fh
from ..utils.error_handlers import ApiError, ok
from ..utils.permissions import current_user, login_required

bp = Blueprint("attachments", __name__, url_prefix="/api/v1")


@bp.post("/tickets/<int:ticket_id>/attachments")
@login_required
def upload(ticket_id):
    u = current_user()
    t = ts.get_ticket_for_user(ticket_id, u)
    files = request.files.getlist("file") or request.files.getlist("files")
    if not files:
        raise ApiError("No file provided (multipart field 'file').", 400, "no_file")
    if len(files) > 5:
        raise ApiError("A maximum of 5 files can be uploaded at once.", 422, "too_many_files")
    mid = request.form.get("message_id")
    internal = request.form.get("is_internal", "").lower() in ("1", "true")
    saved = []
    try:
        for f in files:
            saved.append(ats.save_attachment(t, u, f, int(mid) if mid and mid.isdigit() else None, internal))
        db.session.commit()
    except Exception:
        db.session.rollback()
        for a in saved:  # don't leave orphaned files on disk
            ats.remove_file(fh.resolve_path(current_app.config["UPLOAD_FOLDER"], a.file_path))
        raise
    return ok([a.to_dict() for a in saved], "File uploaded.", 201)


@bp.get("/tickets/<int:ticket_id>/attachments")
@login_required
def list_attachments(ticket_id):
    u = current_user()
    t = ts.get_ticket_for_user(ticket_id, u)
    return ok([a.to_dict() for a in ats.visible_attachments(t, u)])


def _get_att(attachment_id):
    u = current_user()
    a = db.session.get(TicketAttachment, attachment_id)
    if not a:
        raise ApiError("Attachment not found.", 404, "not_found")
    ts.get_ticket_for_user(a.ticket_id, u)  # permission check on parent ticket
    if a.is_internal and u.role == "customer":
        raise ApiError("Attachment not found.", 404, "not_found")
    return a


@bp.get("/attachments/<int:attachment_id>/download")
@login_required
def download(attachment_id):
    a = _get_att(attachment_id)
    path = fh.resolve_path(current_app.config["UPLOAD_FOLDER"], a.file_path)
    try:
        return send_file(path, mimetype=a.mime_type, as_attachment=True, download_name=a.original_filename)
    except FileNotFoundError:
        raise ApiError("File is no longer available.", 404, "file_missing")


@bp.delete("/attachments/<int:attachment_id>")
@login_required
def delete(attachment_id):
    a = _get_att(attachment_id)
    path = ats.delete_attachment(a, current_user())
    db.session.commit()
    ats.remove_file(path)
    return ok(None, "Attachment deleted.")
