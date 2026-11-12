from datetime import datetime

from ..extensions import db

PRIORITIES = ("low", "medium", "high", "critical")
STATUSES = ("open", "assigned", "in_progress", "waiting_for_customer", "resolved", "closed")


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


class Ticket(db.Model):
    __tablename__ = "tickets"
    ticket_id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(30), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey("ticket_categories.category_id"), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum(*PRIORITIES, name="ticket_priority"), nullable=False, default="medium", index=True)
    status = db.Column(db.Enum(*STATUSES, name="ticket_status"), nullable=False, default="open", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)

    customer = db.relationship("User", foreign_keys=[customer_id])
    agent = db.relationship("User", foreign_keys=[assigned_agent_id])
    category = db.relationship("TicketCategory")
    messages = db.relationship("TicketMessage", backref="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    attachments = db.relationship("TicketAttachment", backref="ticket", cascade="all, delete-orphan")
    history = db.relationship("TicketStatusHistory", backref="ticket", cascade="all, delete-orphan", order_by="TicketStatusHistory.changed_at")
    sla = db.relationship("SLARecord", uselist=False, backref="ticket", cascade="all, delete-orphan")

    def to_dict(self, detail=False):
        d = {
            "ticket_id": self.ticket_id,
            "ticket_number": self.ticket_number,
            "customer": self.customer.brief() if self.customer else None,
            "assigned_agent": self.agent.brief() if self.agent else None,
            "category": self.category.to_dict() if self.category else None,
            "subject": self.subject,
            "priority": self.priority,
            "status": self.status,
            "created_at": iso(self.created_at),
            "updated_at": iso(self.updated_at),
            "resolved_at": iso(self.resolved_at),
            "closed_at": iso(self.closed_at),
            "sla": self.sla.to_dict() if self.sla else None,
        }
        if detail:
            d["description"] = self.description
        return d
