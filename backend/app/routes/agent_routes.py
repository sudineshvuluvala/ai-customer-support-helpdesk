from flask import Blueprint, request

from ..extensions import db
from ..models import SavedReply, User
from ..services import analytics_service, audit_service, ticket_service
from ..services.assignment_service import agent_workload
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, roles_required
from ..utils.validators import get_str, json_body, page_params, raise_if

bp = Blueprint("agents", __name__, url_prefix="/api/v1/agents")


@bp.get("/dashboard")
@roles_required("agent")
def dashboard():
    return ok(analytics_service.agent_dashboard(current_user()))


@bp.get("/tickets")
@roles_required("agent")
def tickets():
    page, per_page = page_params()
    q = ticket_service.build_query(current_user(), request.args)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return paginated([t.to_dict() for t in items], page, per_page, total)


@bp.get("/workload")
@roles_required("admin", "agent")
def workload():
    data = agent_workload()
    if current_user().role == "agent":
        data = [w for w in data if w["user_id"] == current_user().user_id]
    return ok(data)


def _own_reply(reply_id):
    r = db.session.get(SavedReply, reply_id)
    if not r or r.created_by != current_user().user_id:
        raise ApiError("Saved reply not found.", 404, "not_found")
    return r


@bp.get("/saved-replies")
@roles_required("agent", "admin")
def list_replies():
    rows = SavedReply.query.filter_by(created_by=current_user().user_id).order_by(SavedReply.title).all()
    return ok([r.to_dict() for r in rows])


@bp.post("/saved-replies")
@roles_required("agent", "admin")
def create_reply():
    d, errors = json_body(), {}
    title = get_str(d, "title", max_len=120, errors=errors)
    content = get_str(d, "reply_content", max_len=5000, errors=errors)
    raise_if(errors)
    r = SavedReply(created_by=current_user().user_id, title=title, reply_content=content)
    db.session.add(r)
    db.session.commit()
    return ok(r.to_dict(), "Saved reply created.", 201)


@bp.put("/saved-replies/<int:reply_id>")
@roles_required("agent", "admin")
def update_reply(reply_id):
    r, d, errors = _own_reply(reply_id), json_body(), {}
    title = get_str(d, "title", max_len=120, errors=errors)
    content = get_str(d, "reply_content", max_len=5000, errors=errors)
    raise_if(errors)
    r.title, r.reply_content = title, content
    db.session.commit()
    return ok(r.to_dict(), "Saved reply updated.")


@bp.delete("/saved-replies/<int:reply_id>")
@roles_required("agent", "admin")
def delete_reply(reply_id):
    db.session.delete(_own_reply(reply_id))
    db.session.commit()
    return ok(None, "Saved reply deleted.")
