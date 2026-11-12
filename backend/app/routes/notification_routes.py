from flask import Blueprint, request

from ..extensions import db
from ..models import Notification
from ..services import notification_service as ns
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, login_required
from ..utils.validators import page_params

bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")


@bp.get("")
@login_required
def list_notifications():
    page, per_page = page_params(15)
    items, total = ns.list_for_user(current_user(), page, per_page, request.args.get("unread") in ("1", "true"))
    return paginated([n.to_dict() for n in items], page, per_page, total, unread_count=ns.unread_count(current_user()))


@bp.patch("/read-all")
@login_required
def read_all():
    Notification.query.filter_by(user_id=current_user().user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return ok({"unread_count": 0}, "All notifications marked as read.")


@bp.patch("/<int:nid>/read")
@login_required
def mark_read(nid):
    n = db.session.get(Notification, nid)
    if not n or n.user_id != current_user().user_id:  # only the intended user
        raise ApiError("Notification not found.", 404, "not_found")
    n.is_read = True
    db.session.commit()
    return ok(n.to_dict())
