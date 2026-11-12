from datetime import datetime

from ..extensions import db
from .ticket import iso


class TicketMessage(db.Model):
    __tablename__ = "ticket_messages"
    message_id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    message_content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.Enum("public", "internal", name="message_type"), nullable=False, default="public")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sender = db.relationship("User")
    attachments = db.relationship("TicketAttachment", backref="message")

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "ticket_id": self.ticket_id,
            "sender": self.sender.brief() if self.sender else None,
            "message_content": self.message_content,
            "message_type": self.message_type,
            "created_at": iso(self.created_at),
            "attachments": [a.to_dict() for a in self.attachments],
        }
