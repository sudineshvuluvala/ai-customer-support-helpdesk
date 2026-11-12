from datetime import datetime

from ..extensions import db
from .ticket import iso


class TicketStatusHistory(db.Model):
    """Ticket history: status, priority and assignment changes (see `event_type`)."""
    __tablename__ = "ticket_status_history"
    history_id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.ticket_id"), nullable=False, index=True)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    event_type = db.Column(db.String(20), nullable=False, default="status")  # status|priority|assignment|created
    old_status = db.Column(db.String(60))
    new_status = db.Column(db.String(60))
    remarks = db.Column(db.String(500))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User")

    def to_dict(self):
        return {
            "history_id": self.history_id,
            "event_type": self.event_type,
            "old_value": self.old_status,
            "new_value": self.new_status,
            "remarks": self.remarks,
            "changed_by": self.user.brief() if self.user else None,
            "changed_at": iso(self.changed_at),
        }
