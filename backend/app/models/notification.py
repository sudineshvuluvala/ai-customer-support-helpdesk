from datetime import datetime

from ..extensions import db
from .ticket import iso


class Notification(db.Model):
    __tablename__ = "notifications"
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    notification_type = db.Column(db.String(40), nullable=False, default="info")
    related_ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.ticket_id"), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "related_ticket_id": self.related_ticket_id,
            "is_read": self.is_read,
            "created_at": iso(self.created_at),
        }
