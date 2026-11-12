from flask import Blueprint

from ..services import analytics_service as an
from ..utils.error_handlers import ok
from ..utils.permissions import current_user, roles_required

bp = Blueprint("analytics", __name__, url_prefix="/api/v1/analytics")


@bp.get("")
@roles_required("admin", "agent")
def overview():
    u = current_user()
    return ok({
        "status_counts": an.status_counts(u),
        "avg_resolution_hours": an.avg_resolution_hours(u),
        "overdue": an.overdue_count(u),
        "priority_distribution": an.priority_distribution(u),
        "category_distribution": an.category_distribution(u),
        "creation_trend": an.creation_trend(14, u),
    })


@bp.get("/tickets")
@roles_required("admin", "agent")
def tickets():
    u = current_user()
    from flask import request
    days = min(max(int(request.args.get("days", 30)) if request.args.get("days", "30").isdigit() else 30, 7), 180)
    return ok({"creation_trend": an.creation_trend(days, u), "by_status": an.status_counts(u),
               "by_priority": an.priority_distribution(u), "by_category": an.category_distribution(u),
               "avg_resolution_hours": an.avg_resolution_hours(u)})


@bp.get("/agents")
@roles_required("admin")
def agents():
    return ok(an.agent_performance())


@bp.get("/sla")
@roles_required("admin", "agent")
def sla():
    from ..models import SLARecord, Ticket
    u = current_user()
    data = an.sla_summary()
    q = Ticket.query.join(SLARecord, SLARecord.ticket_id == Ticket.ticket_id).filter(Ticket.status.notin_(["resolved", "closed"]))
    if u.role == "agent":
        q = q.filter(Ticket.assigned_agent_id == u.user_id)
        data = None
    from ..services import sla_service
    risky = [t.to_dict() for t in q.order_by(SLARecord.resolution_due_at.asc()).limit(50).all()]
    risky = [t for t in risky if t["sla"]["sla_status"] in ("at_risk", "breached")]
    return ok({"summary": data, "at_risk_tickets": risky, "settings": sla_service.get_settings()})
