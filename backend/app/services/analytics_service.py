from collections import OrderedDict
from datetime import datetime, timedelta

from sqlalchemy import func

from ..extensions import db
from ..models import AuditLog, SLARecord, Ticket, TicketCategory, User
from . import sla_service
from .assignment_service import agent_workload

OPEN_STATES = ("open", "assigned", "in_progress", "waiting_for_customer")


def _scope(q, user):
    if user is None or user.role == "admin":
        return q
    if user.role == "agent":
        return q.filter(Ticket.assigned_agent_id == user.user_id)
    return q.filter(Ticket.customer_id == user.user_id)


def status_counts(user=None):
    q = _scope(db.session.query(Ticket.status, func.count(Ticket.ticket_id)), user).group_by(Ticket.status)
    counts = dict(q.all())
    return {s: counts.get(s, 0) for s in ("open", "assigned", "in_progress", "waiting_for_customer", "resolved", "closed")}


def overdue_count(user=None):
    now = datetime.utcnow()
    q = _scope(db.session.query(func.count(Ticket.ticket_id)).join(SLARecord, SLARecord.ticket_id == Ticket.ticket_id), user)
    q = q.filter(Ticket.status.notin_(["resolved", "closed"]),
                 (SLARecord.resolution_due_at < now) | (SLARecord.first_response_at.is_(None) & (SLARecord.response_due_at < now)))
    return q.scalar() or 0


def avg_resolution_hours(user=None):
    q = _scope(db.session.query(Ticket.created_at, Ticket.resolved_at).filter(Ticket.resolved_at.isnot(None)), user)
    rows = q.all()
    if not rows:
        return None
    return round(sum((r - c).total_seconds() for c, r in rows) / len(rows) / 3600, 2)


def distribution(column, user=None):
    q = _scope(db.session.query(column, func.count(Ticket.ticket_id)), user).group_by(column)
    return q.all()


def category_distribution(user=None):
    q = _scope(db.session.query(TicketCategory.category_name, func.count(Ticket.ticket_id))
               .join(Ticket, Ticket.category_id == TicketCategory.category_id), user).group_by(TicketCategory.category_name)
    return [{"label": n, "count": c} for n, c in q.all()]


def priority_distribution(user=None):
    d = dict(distribution(Ticket.priority, user))
    return [{"label": p, "count": d.get(p, 0)} for p in ("low", "medium", "high", "critical")]


def creation_trend(days=14, user=None):
    start = datetime.utcnow().date() - timedelta(days=days - 1)
    q = _scope(db.session.query(func.date(Ticket.created_at), func.count(Ticket.ticket_id))
               .filter(Ticket.created_at >= datetime.combine(start, datetime.min.time())), user).group_by(func.date(Ticket.created_at))
    found = {str(d): c for d, c in q.all()}
    out = OrderedDict()
    for i in range(days):
        d = str(start + timedelta(days=i))
        out[d] = found.get(d, 0)
    return [{"date": d, "count": c} for d, c in out.items()]


def sla_summary():
    statuses = [sla_service.compute_status(s) for s in SLARecord.query.all()]
    total = len(statuses)
    counts = {k: statuses.count(k) for k in ("on_track", "at_risk", "breached", "met")}
    finished = counts["met"] + counts["breached"]
    counts["total"] = total
    counts["compliance_rate"] = round(counts["met"] / finished * 100, 1) if finished else None
    return counts


def recent_activity(limit=10):
    return [a.to_dict() for a in AuditLog.query.order_by(AuditLog.created_at.desc(), AuditLog.log_id.desc()).limit(limit).all()]


def admin_dashboard():
    sc = status_counts()
    return {
        "users": {
            "total": User.query.count(),
            "customers": User.query.filter_by(role="customer").count(),
            "agents": User.query.filter_by(role="agent").count(),
            "admins": User.query.filter_by(role="admin").count(),
        },
        "tickets": {
            "total": sum(sc.values()), **sc,
            "unassigned": Ticket.query.filter(Ticket.assigned_agent_id.is_(None), Ticket.status.in_(OPEN_STATES)).count(),
            "high_priority": Ticket.query.filter(Ticket.priority.in_(["high", "critical"]), Ticket.status.in_(OPEN_STATES)).count(),
            "overdue": overdue_count(),
        },
        "category_distribution": category_distribution(),
        "priority_distribution": priority_distribution(),
        "agent_workload": agent_workload(),
        "avg_resolution_hours": avg_resolution_hours(),
        "creation_trend": creation_trend(14),
        "recent_activity": recent_activity(10),
    }


def agent_dashboard(user):
    sc = status_counts(user)
    base = Ticket.query.filter_by(assigned_agent_id=user.user_id)
    pending = 0
    from ..models import TicketMessage
    for t in base.filter(Ticket.status.in_(OPEN_STATES)).all():
        last = (TicketMessage.query.filter_by(ticket_id=t.ticket_id, message_type="public")
                .order_by(TicketMessage.created_at.desc(), TicketMessage.message_id.desc()).first())
        if (last is None) or last.sender_id == t.customer_id:
            pending += 1
    recent = base.order_by(Ticket.updated_at.desc()).limit(5).all()
    return {
        "tickets": {"total": sum(sc.values()), **sc, "new": base.filter(Ticket.status == "assigned").count(),
                    "high_priority": base.filter(Ticket.priority.in_(["high", "critical"]), Ticket.status.in_(OPEN_STATES)).count(),
                    "overdue": overdue_count(user), "pending_responses": pending},
        "recent_tickets": [t.to_dict() for t in recent],
    }


def customer_dashboard(user):
    sc = status_counts(user)
    recent = Ticket.query.filter_by(customer_id=user.user_id).order_by(Ticket.updated_at.desc()).limit(5).all()
    return {"tickets": {"total": sum(sc.values()), **sc}, "recent_tickets": [t.to_dict() for t in recent]}


def agent_performance():
    out = []
    for w in agent_workload():
        rows = (db.session.query(Ticket.created_at, Ticket.resolved_at)
                .filter(Ticket.assigned_agent_id == w["user_id"], Ticket.resolved_at.isnot(None)).all())
        avg = round(sum((r - c).total_seconds() for c, r in rows) / len(rows) / 3600, 2) if rows else None
        out.append({**w, "resolved_tickets": len(rows), "avg_resolution_hours": avg})
    return out
