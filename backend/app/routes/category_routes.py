from flask import Blueprint, request

from ..extensions import db
from ..models import Ticket, TicketCategory
from ..services import audit_service
from ..utils.error_handlers import ApiError, ok
from ..utils.permissions import current_user, login_required, roles_required
from ..utils.validators import get_str, json_body, raise_if

bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")


@bp.get("")
@login_required
def list_categories():
    q = TicketCategory.query
    if current_user().role != "admin" or request.args.get("active_only") in ("1", "true"):
        q = q.filter_by(is_active=True)
    return ok([c.to_dict() for c in q.order_by(TicketCategory.category_name).all()])


def _fields(d, partial_ok=False):
    errors = {}
    name = get_str(d, "category_name", max_len=100, errors=errors)
    desc = get_str(d, "description", required=False, max_len=255, errors=errors)
    raise_if(errors)
    return name, desc


@bp.post("")
@roles_required("admin")
def create():
    d = json_body()
    name, desc = _fields(d)
    if TicketCategory.query.filter(TicketCategory.category_name.ilike(name)).first():
        raise ApiError("Category already exists.", 409, "duplicate", {"category_name": "Already exists."})
    c = TicketCategory(category_name=name, description=desc, is_active=bool(d.get("is_active", True)))
    db.session.add(c)
    db.session.flush()
    audit_service.audit(current_user(), "category_created", "category", c.category_id, name)
    db.session.commit()
    return ok(c.to_dict(), "Category created.", 201)


@bp.put("/<int:cid>")
@roles_required("admin")
def update(cid):
    c = db.session.get(TicketCategory, cid)
    if not c:
        raise ApiError("Category not found.", 404, "not_found")
    d = json_body()
    name, desc = _fields(d)
    dup = TicketCategory.query.filter(TicketCategory.category_name.ilike(name), TicketCategory.category_id != cid).first()
    if dup:
        raise ApiError("Category name already exists.", 409, "duplicate", {"category_name": "Already exists."})
    c.category_name, c.description = name, desc
    if "is_active" in d:
        c.is_active = bool(d["is_active"])
    audit_service.audit(current_user(), "category_updated", "category", cid, name)
    db.session.commit()
    return ok(c.to_dict(), "Category updated.")


@bp.delete("/<int:cid>")
@roles_required("admin")
def delete(cid):
    c = db.session.get(TicketCategory, cid)
    if not c:
        raise ApiError("Category not found.", 404, "not_found")
    if Ticket.query.filter_by(category_id=cid).count():
        raise ApiError("Category is used by existing tickets and cannot be deleted. Deactivate it instead.", 409, "in_use")
    audit_service.audit(current_user(), "category_deleted", "category", cid, c.category_name)
    db.session.delete(c)
    db.session.commit()
    return ok(None, "Category deleted.")
