import os
import uuid
from flask import Blueprint, current_app, request, send_from_directory
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import KnowledgeArticle, Ticket, User
from ..services import analytics_service, audit_service
from ..utils import file_helpers as fh
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, login_required, roles_required
from ..utils.validators import get_str, json_body, like_escape, page_params, raise_if, validate_email, validate_password

bp = Blueprint("users", __name__, url_prefix="/api/v1")


def user_list_query(role=None):
    q = User.query
    if role:
        q = q.filter(User.role == role)
    elif request.args.get("role") in ("admin", "agent", "customer"):
        q = q.filter(User.role == request.args["role"])
    if request.args.get("status") in ("active", "inactive"):
        q = q.filter(User.account_status == request.args["status"])
    term = (request.args.get("q") or "").strip()
    if term:
        like = f"%{like_escape(term)}%"
        q = q.filter(User.name.like(like, escape="\\") | User.email.like(like, escape="\\"))
    return q.order_by(User.created_at.desc())


def list_users_response(role=None):
    page, per_page = page_params()
    q = user_list_query(role)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return paginated([u.to_dict() for u in items], page, per_page, total)


@bp.get("/users")
@roles_required("admin")
def list_users():
    return list_users_response()


@bp.get("/users/profile")
@login_required
def get_profile():
    return ok(current_user().to_dict())


@bp.put("/users/profile")
@login_required
def update_profile():
    u, d = current_user(), json_body()
    errors = {}
    if "name" in d:
        name = get_str(d, "name", min_len=2, max_len=120, errors=errors)
        if name:
            u.name = name
    if d.get("new_password"):
        if not u.check_password(d.get("current_password") or ""):
            errors["current_password"] = "Current password is incorrect."
        else:
            err = validate_password(d["new_password"])
            if err:
                errors["new_password"] = err
            else:
                u.set_password(d["new_password"])
    raise_if(errors)
    audit_service.audit(u, "profile_updated", "user", u.user_id, "Profile updated")
    db.session.commit()
    return ok(u.to_dict(), "Profile updated.")


@bp.post("/users/profile/photo")
@login_required
def upload_profile_photo():
    u = current_user()
    if "photo" not in request.files:
        raise ApiError("No photo uploaded (file field 'photo').", 400, "no_file")
    f = request.files["photo"]
    data, ext, mime, orig = fh.validate_upload(f, allowed={"png", "jpg", "jpeg"}, max_bytes=2 * 1024 * 1024)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"user_{u.user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    # Clean old photo if exists
    if u.profile_photo:
        old_path = os.path.join(upload_dir, u.profile_photo)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass

    with open(filepath, "wb") as out:
        out.write(data)

    u.profile_photo = filename
    audit_service.audit(u, "profile_photo_updated", "user", u.user_id, "Profile photo updated")
    db.session.commit()
    return ok(u.to_dict(), "Profile photo updated.")


@bp.delete("/users/profile/photo")
@login_required
def delete_profile_photo():
    u = current_user()
    if u.profile_photo:
        upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
        old_path = os.path.join(upload_dir, u.profile_photo)
        if os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except Exception:
                pass
        u.profile_photo = None
        audit_service.audit(u, "profile_photo_deleted", "user", u.user_id, "Profile photo removed")
        db.session.commit()
    return ok(u.to_dict(), "Profile photo removed.")


@bp.get("/users/avatar/<filename>")
def get_avatar(filename):
    safe_name = secure_filename(filename)
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
    return send_from_directory(upload_dir, safe_name)


@bp.get("/users/<int:user_id>")
@login_required
def get_user(user_id):
    me = current_user()
    target = db.session.get(User, user_id)
    if not target:
        raise ApiError("User not found.", 404, "not_found")
    allowed = me.role == "admin" or me.user_id == user_id
    if not allowed and me.role == "agent" and target.role == "customer":
        allowed = Ticket.query.filter_by(customer_id=user_id, assigned_agent_id=me.user_id).first() is not None
    if not allowed:
        raise ApiError("User not found.", 404, "not_found")
    return ok(target.to_dict())


@bp.get("/customer/dashboard")
@roles_required("customer")
def customer_dashboard():
    from ..services import notification_service as ns
    d = analytics_service.customer_dashboard(current_user())
    arts = KnowledgeArticle.query.filter_by(status="published").order_by(KnowledgeArticle.updated_at.desc()).limit(4).all()
    d["recommended_articles"] = [a.to_dict(full=False) for a in arts]
    items, _ = ns.list_for_user(current_user(), 1, 5)
    d["notifications"] = [n.to_dict() for n in items]
    d["unread_notifications"] = ns.unread_count(current_user())
    return ok(d)
