from flask import Blueprint

from ..extensions import db
from ..services import conversation_service as cs, ticket_service as ts
from ..utils.error_handlers import ok
from ..utils.permissions import current_user, login_required
from ..utils.validators import get_str, json_body

bp = Blueprint("messages", __name__, url_prefix="/api/v1/tickets")


@bp.get("/<int:ticket_id>/messages")
@login_required
def list_messages(ticket_id):
    u = current_user()
    t = ts.get_ticket_for_user(ticket_id, u)
    return ok([m.to_dict() if u.role != "customer" else _public(m) for m in cs.list_messages(t, u)])


def _public(m):
    d = m.to_dict()
    d["attachments"] = [a for a in d["attachments"] if not a["is_internal"]]
    return d


@bp.post("/<int:ticket_id>/messages")
@login_required
def create_message(ticket_id):
    u, d = current_user(), json_body()
    t = ts.get_ticket_for_user(ticket_id, u)
    content = get_str(d, "message_content", max_len=10000)
    m = cs.add_message(t, u, content, d.get("message_type", "public"))
    db.session.commit()
    return ok(m.to_dict(), "Message sent.", 201)
