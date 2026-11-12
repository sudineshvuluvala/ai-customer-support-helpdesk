from ..extensions import db
from ..models import TicketMessage
from ..utils.error_handlers import ApiError
from . import audit_service, notification_service as ns, sla_service
from .ticket_service import change_status, history


def list_messages(ticket, user):
    q = TicketMessage.query.filter_by(ticket_id=ticket.ticket_id)
    if user.role == "customer":
        q = q.filter_by(message_type="public")  # internal notes are NEVER visible to customers
    return q.order_by(TicketMessage.created_at.asc(), TicketMessage.message_id.asc()).all()


def add_message(ticket, user, content, message_type="public"):
    if message_type not in ("public", "internal"):
        raise ApiError("Validation failed.", 422, "validation_error", {"message_type": "Must be public or internal."})
    if message_type == "internal" and user.role == "customer":
        raise ApiError("Customers cannot create internal notes.", 403, "forbidden")
    if ticket.status == "closed":
        raise ApiError("This ticket is closed. Reopen it to continue the conversation.", 409, "ticket_closed")
    msg = TicketMessage(ticket_id=ticket.ticket_id, sender_id=user.user_id, message_content=content, message_type=message_type)
    db.session.add(msg)
    db.session.flush()
    ticket.updated_at = msg.created_at
    if message_type == "internal":
        audit_service.audit(user, "internal_note", "ticket", ticket.ticket_id, "Internal note added")
        return msg
    if user.role == "customer":
        if ticket.status == "resolved":      # request further assistance
            change_status(ticket, "assigned" if ticket.assigned_agent_id else "open", user, "Customer replied after resolution", system=True)
        elif ticket.status == "waiting_for_customer":
            change_status(ticket, "in_progress", user, "Customer replied", system=True)
        ns.notify_ticket_participants(ticket, user, "Customer replied", f"New reply on {ticket.ticket_number}.", "customer_reply")
    else:
        sla_service.mark_first_response(ticket)
        if ticket.status in ("open", "assigned"):
            change_status(ticket, "in_progress", user, "Agent responded", system=True)
        # Notify customer with actual agent response content
        sender_label = "Administrator" if user.role == "admin" else f"Agent {user.name}"
        email_body = f"{sender_label} has sent you a new response on ticket #{ticket.ticket_number} ({ticket.subject}):\n\n\"{content}\""
        ns.notify_ticket_participants(ticket, user, f"New response from {sender_label}", email_body, "agent_reply")
    return msg
