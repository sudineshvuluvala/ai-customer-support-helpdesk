from sqlalchemy import func

from ..extensions import db
from ..models import Ticket, User
from ..utils.error_handlers import ApiError
from . import audit_service, notification_service as ns
from .ticket_service import history


def agent_workload():
    open_states = ("open", "assigned", "in_progress", "waiting_for_customer")
    counts = dict(db.session.query(Ticket.assigned_agent_id, func.count(Ticket.ticket_id))
                  .filter(Ticket.status.in_(open_states), Ticket.assigned_agent_id.isnot(None))
                  .group_by(Ticket.assigned_agent_id).all())
    total = dict(db.session.query(Ticket.assigned_agent_id, func.count(Ticket.ticket_id))
                 .filter(Ticket.assigned_agent_id.isnot(None)).group_by(Ticket.assigned_agent_id).all())
    out = []
    for a in User.query.filter_by(role="agent").order_by(User.name).all():
        out.append({**a.brief(), "account_status": a.account_status,
                    "active_tickets": counts.get(a.user_id, 0), "total_tickets": total.get(a.user_id, 0)})
    return out


def assign_ticket(ticket, agent_id, admin, remarks=None):
    agent = db.session.get(User, agent_id) if agent_id else None
    if not agent or agent.role != "agent":
        raise ApiError("Selected agent does not exist.", 422, "validation_error", {"agent_id": "Agent not found."})
    if not agent.is_active:
        raise ApiError("Selected agent is inactive.", 422, "validation_error", {"agent_id": "Agent is inactive."})
    if ticket.status == "closed":
        raise ApiError("Closed tickets cannot be assigned.", 409, "not_editable")
    if ticket.assigned_agent_id == agent.user_id:
        raise ApiError("Ticket is already assigned to this agent.", 409, "no_change")
    prev = ticket.agent
    ticket.assigned_agent_id = agent.user_id
    ticket.agent = agent
    reassign = prev is not None
    old_status = ticket.status
    if ticket.status == "open":
        ticket.status = "assigned"
        history(ticket, admin, "status", old_status, "assigned", "Auto-set on assignment")
    history(ticket, admin, "assignment", prev.name if prev else None, agent.name, remarks or ("Reassigned" if reassign else "Assigned"))
    audit_service.audit(admin, "ticket_reassigned" if reassign else "ticket_assigned", "ticket", ticket.ticket_id,
                        f"{ticket.ticket_number} -> {agent.email}")
    ns.notify(agent, "Ticket assigned to you", f"{ticket.ticket_number}: {ticket.subject}", "ticket_assigned", ticket.ticket_id)
    if prev and prev.user_id != agent.user_id:
        ns.notify(prev, "Ticket reassigned", f"{ticket.ticket_number} was reassigned to {agent.name}.", "ticket_reassigned", ticket.ticket_id, email=False)
    ns.notify(ticket.customer, "Agent assigned" if not reassign else "Ticket reassigned",
              f"{ticket.ticket_number} is now handled by {agent.name}.", "ticket_reassigned" if reassign else "ticket_assigned", ticket.ticket_id)
    return ticket
