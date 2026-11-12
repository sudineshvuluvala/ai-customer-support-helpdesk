import uuid
from datetime import datetime

from sqlalchemy import or_

from ..extensions import db
from ..models import PRIORITIES, STATUSES, Ticket, TicketCategory, TicketStatusHistory
from ..utils.error_handlers import ApiError
from ..utils.validators import like_escape
from . import audit_service, notification_service as ns, sla_service

STAFF_TRANSITIONS = {
    "open": {"assigned", "in_progress", "waiting_for_customer", "resolved", "closed"},
    "assigned": {"open", "in_progress", "waiting_for_customer", "resolved", "closed"},
    "in_progress": {"assigned", "waiting_for_customer", "resolved", "closed"},
    "waiting_for_customer": {"in_progress", "resolved", "closed"},
    "resolved": {"in_progress", "closed"},
    "closed": {"in_progress"},  # reopen
}
AGENT_FORBIDDEN_TARGETS = {"open", "assigned"}  # only admins (assignment flow) set these
CUSTOMER_TRANSITIONS = {
    "resolved": {"closed", "open"},
    "closed": {"open"},
    "open": {"closed"},
    "assigned": {"closed"},
    "in_progress": {"closed"},
    "waiting_for_customer": {"closed"},
}
STATUS_LABELS = {s: s.replace("_", " ").title() for s in STATUSES}


def history(ticket, user, event_type, old, new, remarks=None):
    db.session.add(TicketStatusHistory(
        ticket=ticket, changed_by=user.user_id, event_type=event_type,
        old_status=old, new_status=new, remarks=(remarks or "")[:500] or None,
    ))


def get_ticket_for_user(ticket_id, user):
    """Central ownership/assignment check. Non-owners get 404 so IDs can't be enumerated."""
    t = db.session.get(Ticket, ticket_id)
    if not t:
        raise ApiError("Ticket not found.", 404, "not_found")
    if user.role == "admin":
        return t
    if user.role == "customer" and t.customer_id == user.user_id:
        return t
    if user.role == "agent" and t.assigned_agent_id == user.user_id:
        return t
    raise ApiError("Ticket not found.", 404, "not_found")


def create_ticket(customer, subject, description, category_id, priority, creator=None):
    cat = db.session.get(TicketCategory, category_id) if category_id else None
    if not cat or not cat.is_active:
        raise ApiError("Validation failed.", 422, "validation_error", {"category_id": "Select an active category."})
    if priority not in PRIORITIES:
        raise ApiError("Validation failed.", 422, "validation_error", {"priority": f"Must be one of {', '.join(PRIORITIES)}."})
    if customer.role == "customer" and priority == "critical":
        raise ApiError("Validation failed.", 422, "validation_error", {"priority": "Customers cannot select Critical priority."})
    t = Ticket(ticket_number="TMP-" + uuid.uuid4().hex[:12], customer_id=customer.user_id, category_id=cat.category_id,
               subject=subject, description=description, priority=priority, status="open", created_at=datetime.utcnow())
    db.session.add(t)
    db.session.flush()
    # Unique number derived from the primary key -> race-free: TKT-2026-00001
    t.ticket_number = f"TKT-{t.created_at.year}-{t.ticket_id:05d}"
    sla_service.create_sla(t)
    history(t, creator or customer, "created", None, "open", "Ticket created")
    audit_service.audit(creator or customer, "ticket_created", "ticket", t.ticket_id, t.ticket_number)
    ns.notify(customer, "Ticket created", f"Your ticket {t.ticket_number} was created.", "ticket_created", t.ticket_id)
    ns.notify_admins(t, "New ticket", f"{t.ticket_number}: {t.subject}", "ticket_created", exclude=creator)
    return t


def update_ticket(ticket, user, data):
    if user.role == "customer" and (ticket.status != "open" or ticket.assigned_agent_id):
        raise ApiError("You can only edit a ticket before it is assigned.", 409, "not_editable")
    if ticket.status == "closed":
        raise ApiError("Closed tickets cannot be edited.", 409, "not_editable")
    changed = []
    if "subject" in data:
        ticket.subject = data["subject"]; changed.append("subject")
    if "description" in data:
        ticket.description = data["description"]; changed.append("description")
    if "category_id" in data:
        cat = db.session.get(TicketCategory, data["category_id"])
        if not cat or not cat.is_active:
            raise ApiError("Validation failed.", 422, "validation_error", {"category_id": "Select an active category."})
        ticket.category_id = cat.category_id; changed.append("category")
    if changed:
        audit_service.audit(user, "ticket_updated", "ticket", ticket.ticket_id, "Updated: " + ", ".join(changed))
    return ticket


def change_status(ticket, new_status, user, remarks=None, system=False):
    if new_status not in STATUSES:
        raise ApiError("Validation failed.", 422, "validation_error", {"status": f"Must be one of {', '.join(STATUSES)}."})
    old = ticket.status
    if new_status == old:
        raise ApiError(f"Ticket is already {STATUS_LABELS[old]}.", 409, "invalid_transition")
    if system:  # automatic workflow transition (e.g. customer reply) - not a manual role action
        allowed = {new_status}
    elif user.role == "customer":
        allowed = CUSTOMER_TRANSITIONS.get(old, set())
        if new_status == "open" and ticket.assigned_agent_id:
            new_status = "assigned"  # reopened tickets return to their agent
    elif user.role == "agent":
        allowed = STAFF_TRANSITIONS.get(old, set()) - AGENT_FORBIDDEN_TARGETS
    else:
        allowed = STAFF_TRANSITIONS.get(old, set())
    check = "open" if (user.role == "customer" and new_status == "assigned" and not system) else new_status
    if check not in allowed:
        raise ApiError(f"Transition {STATUS_LABELS[old]} -> {STATUS_LABELS[new_status]} is not allowed for your role.", 409, "invalid_transition")
    if new_status in ("assigned", "in_progress") and not ticket.assigned_agent_id and new_status == "assigned":
        raise ApiError("Assign an agent first.", 409, "invalid_transition")
    now = datetime.utcnow()
    ticket.status = new_status
    if new_status == "resolved":
        ticket.resolved_at = now
        sla_service.mark_resolved(ticket, now)
    elif new_status == "closed":
        ticket.closed_at = now
        if not ticket.resolved_at:
            ticket.resolved_at = now
            sla_service.mark_resolved(ticket, now)
    if old in ("resolved", "closed") and new_status not in ("resolved", "closed"):
        ticket.resolved_at = None
        ticket.closed_at = None
        sla_service.reopen(ticket)
    history(ticket, user, "status", old, new_status, remarks)
    audit_service.audit(user, "ticket_status", "ticket", ticket.ticket_id, f"{old} -> {new_status}")
    label = STATUS_LABELS[new_status]
    ntype = {"resolved": "ticket_resolved", "closed": "ticket_closed"}.get(new_status, "status_changed")
    ns.notify_ticket_participants(ticket, user, f"Ticket {label}", f"{ticket.ticket_number} is now {label}.", ntype)
    if user.role == "customer" and old in ("resolved", "closed"):
        ns.notify_admins(ticket, "Ticket reopened", f"{ticket.ticket_number} was reopened by the customer.", "status_changed")
    return ticket


def change_priority(ticket, new_priority, user, remarks=None):
    if new_priority not in PRIORITIES:
        raise ApiError("Validation failed.", 422, "validation_error", {"priority": f"Must be one of {', '.join(PRIORITIES)}."})
    if user.role == "customer":
        raise ApiError("Customers cannot change priority.", 403, "forbidden")
    if ticket.status == "closed":
        raise ApiError("Closed tickets cannot be changed.", 409, "not_editable")
    old = ticket.priority
    if old == new_priority:
        raise ApiError(f"Priority is already {old}.", 409, "no_change")
    ticket.priority = new_priority
    sla_service.recompute_due_dates(ticket)
    history(ticket, user, "priority", old, new_priority, remarks)
    audit_service.audit(user, "ticket_priority", "ticket", ticket.ticket_id, f"{old} -> {new_priority}")
    ns.notify_ticket_participants(ticket, user, "Priority changed", f"{ticket.ticket_number} priority is now {new_priority}.", "priority_changed")
    return ticket


def build_query(user, args):
    q = Ticket.query
    if user.role == "customer":
        q = q.filter(Ticket.customer_id == user.user_id)
    elif user.role == "agent":
        q = q.filter(Ticket.assigned_agent_id == user.user_id)
    term = (args.get("q") or "").strip()
    if term:
        like = f"%{like_escape(term)}%"
        q = q.filter(or_(Ticket.subject.like(like, escape="\\"), Ticket.ticket_number.like(like, escape="\\"),
                         Ticket.description.like(like, escape="\\")))
    if args.get("status"):
        statuses = [s for s in args["status"].split(",") if s in STATUSES]
        if statuses:
            q = q.filter(Ticket.status.in_(statuses))
    if args.get("priority") in PRIORITIES:
        q = q.filter(Ticket.priority == args["priority"])
    if args.get("category_id", "").isdigit():
        q = q.filter(Ticket.category_id == int(args["category_id"]))
    if user.role == "admin":
        if args.get("agent_id", "").isdigit():
            q = q.filter(Ticket.assigned_agent_id == int(args["agent_id"]))
        if args.get("customer_id", "").isdigit():
            q = q.filter(Ticket.customer_id == int(args["customer_id"]))
        if args.get("unassigned") in ("1", "true"):
            q = q.filter(Ticket.assigned_agent_id.is_(None))
    if args.get("overdue") in ("1", "true"):
        from ..models import SLARecord
        now = datetime.utcnow()
        q = q.join(SLARecord, SLARecord.ticket_id == Ticket.ticket_id).filter(
            Ticket.status.notin_(["resolved", "closed"]),
            or_(SLARecord.resolution_due_at < now, (SLARecord.first_response_at.is_(None)) & (SLARecord.response_due_at < now)))
    sort = args.get("sort", "created_at")
    sort_cols = {"created_at": Ticket.created_at, "updated_at": Ticket.updated_at, "priority": Ticket.priority,
                 "status": Ticket.status, "ticket_number": Ticket.ticket_number, "subject": Ticket.subject}
    col = sort_cols.get(sort, Ticket.created_at)
    q = q.order_by(col.asc() if args.get("order") == "asc" else col.desc(), Ticket.ticket_id.desc())
    return q
