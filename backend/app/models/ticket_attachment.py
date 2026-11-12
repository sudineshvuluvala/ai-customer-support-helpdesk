from datetime import datetime

from ..extensions import db
from .ticket import iso


class TicketAttachment(db.Model):
    __tablename__ = "ticket_attachments"
    attachment_id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    message_id = db.Column(db.Integer, db.ForeignKey("ticket_messages.message_id"), nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_path = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_internal = db.Column(db.Boolean, nullable=False, default=False)

    uploader = db.relationship("User")

    def to_dict(self):
        return {
            "attachment_id": self.attachment_id,
            "ticket_id": self.ticket_id,
            "message_id": self.message_id,
            "uploaded_by": self.uploader.brief() if self.uploader else None,
            "original_filename": self.original_filename,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "uploaded_at": iso(self.uploaded_at),
            "is_internal": self.is_internal,
        }
