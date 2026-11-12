from ..extensions import db
from .ticket import iso


class SLARecord(db.Model):
    __tablename__ = "sla_records"
    sla_id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.ticket_id"), nullable=False, unique=True)
    response_due_at = db.Column(db.DateTime, nullable=False)
    resolution_due_at = db.Column(db.DateTime, nullable=False)
    first_response_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    sla_status = db.Column(db.Enum("on_track", "at_risk", "breached", "met", name="sla_status"), nullable=False, default="on_track", index=True)

    def to_dict(self):
        from ..services.sla_service import compute_status
        return {
            "response_due_at": iso(self.response_due_at),
            "resolution_due_at": iso(self.resolution_due_at),
            "first_response_at": iso(self.first_response_at),
            "resolved_at": iso(self.resolved_at),
            "sla_status": compute_status(self),
        }
