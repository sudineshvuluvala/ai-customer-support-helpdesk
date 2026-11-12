from ..extensions import db
from ..models import Notification, User
from . import email_service


def notify(user, title, message, ntype="info", ticket_id=None, email=True, cta_text=None, cta_url=None):
    if not user:
        return None
    n = Notification(user_id=user.user_id, title=title, message=message[:500], notification_type=ntype, related_ticket_id=ticket_id)
    db.session.add(n)
    if email and user.email:
        try:
            paragraphs = [message]
            if ticket_id:
                paragraphs.append(f"Related Ticket ID: #{ticket_id}")
            html_body = email_service.render_email_template(
                title=title,
                headline=title,
                paragraphs=paragraphs,
                cta_text=cta_text or ("View Ticket" if ticket_id else "Open Helpdesk Portal"),
                cta_url=cta_url or f"http://localhost:5173/tickets/{ticket_id}" if ticket_id else "http://localhost:5173"
            )
            email_service.send_email(user.email, f"[Helpdesk] {title}", message, html_body=html_body)
        except Exception:
            pass
    return n


def notify_ticket_participants(ticket, actor, title, message, ntype):
    """Notify the customer and assigned agent, except the person who acted."""
    seen = set()
    for u in (ticket.customer, ticket.agent):
        if u and u.user_id != (actor.user_id if actor else None) and u.user_id not in seen and u.is_active:
            seen.add(u.user_id)
            notify(u, title, message, ntype, ticket.ticket_id)


def notify_admins(ticket, title, message, ntype, exclude=None):
    for a in User.query.filter_by(role="admin", account_status="active").all():
        if not exclude or a.user_id != exclude.user_id:
            notify(a, title, message, ntype, ticket.ticket_id, email=False)


def list_for_user(user, page, per_page, unread_only=False):
    q = Notification.query.filter_by(user_id=user.user_id)
    if unread_only:
        q = q.filter_by(is_read=False)
    total = q.count()
    items = q.order_by(Notification.created_at.desc(), Notification.notification_id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def unread_count(user):
    return Notification.query.filter_by(user_id=user.user_id, is_read=False).count()
