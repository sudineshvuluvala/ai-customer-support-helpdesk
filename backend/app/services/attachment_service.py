import os

from flask import current_app

from ..extensions import db
from ..models import TicketAttachment, TicketMessage
from ..utils import file_helpers as fh
from ..utils.error_handlers import ApiError
from . import audit_service


def save_attachment(ticket, user, file_storage, message_id=None, is_internal=False):
    cfg = current_app.config
    if ticket.status == "closed":
        raise ApiError("Cannot upload to a closed ticket.", 409, "ticket_closed")
    if is_internal and user.role == "customer":
        raise ApiError("Customers cannot upload internal files.", 403, "forbidden")
    if message_id:
        msg = db.session.get(TicketMessage, message_id)
        if not msg or msg.ticket_id != ticket.ticket_id:
            raise ApiError("Message does not belong to this ticket.", 422, "validation_error", {"message_id": "Invalid message."})
        if user.role == "customer" and msg.message_type == "internal":
            raise ApiError("Invalid message.", 422, "validation_error")
    data, ext, mime, original = fh.validate_upload(file_storage, cfg["ALLOWED_EXTENSIONS"], cfg["MAX_UPLOAD_MB"] * 1024 * 1024)
    stored, rel = fh.store_file(cfg["UPLOAD_FOLDER"], ticket.ticket_id, data, ext)
    att = TicketAttachment(ticket_id=ticket.ticket_id, message_id=message_id, uploaded_by=user.user_id,
                           original_filename=original, stored_filename=stored, file_path=rel,
                           mime_type=mime, file_size=len(data), is_internal=is_internal)
    db.session.add(att)
    audit_service.audit(user, "attachment_uploaded", "ticket", ticket.ticket_id, original)
    return att


def visible_attachments(ticket, user):
    q = TicketAttachment.query.filter_by(ticket_id=ticket.ticket_id)
    if user.role == "customer":
        q = q.filter_by(is_internal=False)
    return q.order_by(TicketAttachment.uploaded_at.asc()).all()


def delete_attachment(att, user):
    if user.role != "admin" and att.uploaded_by != user.user_id:
        raise ApiError("You can only delete your own attachments.", 403, "forbidden")
    if att.ticket.status == "closed" and user.role != "admin":
        raise ApiError("Cannot modify a closed ticket.", 409, "ticket_closed")
    path = fh.resolve_path(current_app.config["UPLOAD_FOLDER"], att.file_path)
    db.session.delete(att)
    audit_service.audit(user, "attachment_deleted", "ticket", att.ticket_id, att.original_filename)
    return path


def remove_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
