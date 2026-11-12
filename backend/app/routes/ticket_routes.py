from flask import Blueprint, request

from ..extensions import db
from ..services import assignment_service, audit_service, sla_service, ticket_service as ts
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, login_required, roles_required
from ..utils.validators import get_str, json_body, page_params, raise_if

bp = Blueprint("tickets", __name__, url_prefix="/api/v1/tickets")


def _detail(t):
    d = t.to_dict(detail=True)
    d["is_overdue"] = sla_service.is_overdue(t)
    return d


@bp.post("")
@roles_required("customer", "admin")
def create():
    u, d, errors = current_user(), json_body(), {}
    subject = get_str(d, "subject", min_len=5, max_len=200, errors=errors)
    desc = get_str(d, "description", min_len=10, max_len=10000, errors=errors)
    raise_if(errors)
    customer = u
    if u.role == "admin":  # admin may log a ticket on behalf of a customer
        from ..models import User
        customer = db.session.get(User, d.get("customer_id") or 0)
        if not customer or customer.role != "customer":
            raise ApiError("Validation failed.", 422, "validation_error", {"customer_id": "Select a valid customer."})
    cat = d.get("category_id")
    t = ts.create_ticket(customer, subject, desc, int(cat) if str(cat).isdigit() else None, d.get("priority", "medium"), creator=u)
    db.session.commit()
    return ok(_detail(t), f"Ticket {t.ticket_number} created.", 201)


@bp.get("")
@login_required
def list_tickets():
    page, per_page = page_params()
    q = ts.build_query(current_user(), request.args)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return paginated([t.to_dict() for t in items], page, per_page, total)


@bp.get("/<int:ticket_id>")
@login_required
def get_ticket(ticket_id):
    return ok(_detail(ts.get_ticket_for_user(ticket_id, current_user())))


@bp.put("/<int:ticket_id>")
@login_required
def update(ticket_id):
    u, d = current_user(), json_body()
    t = ts.get_ticket_for_user(ticket_id, u)
    errors, clean = {}, {}
    if "subject" in d:
        clean["subject"] = get_str(d, "subject", min_len=5, max_len=200, errors=errors)
    if "description" in d:
        clean["description"] = get_str(d, "description", min_len=10, max_len=10000, errors=errors)
    if "category_id" in d:
        clean["category_id"] = int(d["category_id"]) if str(d["category_id"]).isdigit() else 0
    raise_if(errors)
    ts.update_ticket(t, u, clean)
    db.session.commit()
    return ok(_detail(t), "Ticket updated.")


@bp.patch("/<int:ticket_id>/status")
@login_required
def set_status(ticket_id):
    u, d = current_user(), json_body()
    t = ts.get_ticket_for_user(ticket_id, u)
    ts.change_status(t, d.get("status"), u, (d.get("remarks") or "")[:500])
    db.session.commit()
    return ok(_detail(t), "Status updated.")


@bp.patch("/<int:ticket_id>/priority")
@roles_required("admin", "agent")
def set_priority(ticket_id):
    u, d = current_user(), json_body()
    t = ts.get_ticket_for_user(ticket_id, u)
    ts.change_priority(t, d.get("priority"), u, (d.get("remarks") or "")[:500])
    db.session.commit()
    return ok(_detail(t), "Priority updated.")


@bp.patch("/<int:ticket_id>/assign")
@roles_required("admin")
def assign(ticket_id):
    u, d = current_user(), json_body()
    t = ts.get_ticket_for_user(ticket_id, u)
    agent_id = d.get("agent_id")
    assignment_service.assign_ticket(t, int(agent_id) if str(agent_id).isdigit() else None, u, (d.get("remarks") or "")[:500])
    db.session.commit()
    return ok(_detail(t), "Ticket assigned.")


@bp.get("/<int:ticket_id>/history")
@login_required
def history(ticket_id):
    t = ts.get_ticket_for_user(ticket_id, current_user())
    return ok([h.to_dict() for h in t.history])
