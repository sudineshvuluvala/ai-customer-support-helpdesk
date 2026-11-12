import csv
import io

from flask import Blueprint, Response, request

from ..extensions import db
from ..models import AuditLog, Ticket, User
from ..services import analytics_service, audit_service, auth_service, sla_service, ticket_service
from ..services.assignment_service import agent_workload
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, roles_required
from ..utils.validators import get_str, json_body, page_params, raise_if
from .user_routes import list_users_response

bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@bp.get("/dashboard")
@roles_required("admin")
def dashboard():
    return ok(analytics_service.admin_dashboard())


@bp.get("/users")
@roles_required("admin")
def users():
    return list_users_response()


@bp.get("/agents")
@roles_required("admin")
def agents():
    if request.args.get("workload") in ("1", "true"):
        return ok(agent_workload())
    return list_users_response(role="agent")


def _create(role):
    d = json_body()
    user = auth_service.register_user(d.get("name"), d.get("email"), d.get("password"), role=role)
    audit_service.audit(current_user(), "user_created", "user", user.user_id, f"{role} account created: {user.email}")
    db.session.commit()
    return ok(user.to_dict(), f"{role.title()} account created.", 201)


@bp.post("/agents")
@roles_required("admin")
def create_agent():
    return _create("agent")


@bp.post("/users")
@roles_required("admin")
def create_user():
    role = (request.get_json(silent=True) or {}).get("role", "customer")
    if role not in ("admin", "agent", "customer"):
        raise ApiError("Validation failed.", 422, "validation_error", {"role": "Invalid role."})
    return _create(role)


@bp.put("/users/<int:user_id>")
@roles_required("admin")
def update_user(user_id):
    u = db.session.get(User, user_id)
    if not u:
        raise ApiError("User not found.", 404, "not_found")
    d, errors = json_body(), {}
    if "name" in d:
        n = get_str(d, "name", min_len=2, max_len=120, errors=errors)
        if n:
            u.name = n
    if "email" in d:
        from ..utils.validators import validate_email
        email = str(d["email"]).strip().lower()
        if not validate_email(email):
            errors["email"] = "A valid email is required."
        elif email != u.email:
            if User.query.filter_by(email=email).first():
                errors["email"] = "Email already registered."
            else:
                u.email = email
    if "role" in d and d["role"] != u.role:
        if d["role"] not in ("admin", "agent", "customer"):
            errors["role"] = "Invalid role."
        elif u.user_id == current_user().user_id:
            errors["role"] = "You cannot change your own role."
        else:
            u.role = d["role"]
    raise_if(errors)
    audit_service.audit(current_user(), "user_updated", "user", u.user_id, f"Updated {u.email}")
    db.session.commit()
    return ok(u.to_dict(), "User updated.")


@bp.patch("/users/<int:user_id>/status")
@roles_required("admin")
def set_status(user_id):
    u = db.session.get(User, user_id)
    if not u:
        raise ApiError("User not found.", 404, "not_found")
    status = json_body().get("account_status")
    if status not in ("active", "inactive"):
        raise ApiError("Validation failed.", 422, "validation_error", {"account_status": "Must be active or inactive."})
    if u.user_id == current_user().user_id and status == "inactive":
        raise ApiError("You cannot deactivate your own account.", 409, "invalid_operation")
    u.account_status = status
    audit_service.audit(current_user(), "user_" + ("activated" if status == "active" else "deactivated"), "user", u.user_id, u.email)
    db.session.commit()
    return ok(u.to_dict(), f"Account {status}.")


@bp.get("/tickets")
@roles_required("admin")
def tickets():
    page, per_page = page_params()
    q = ticket_service.build_query(current_user(), request.args)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return paginated([t.to_dict() for t in items], page, per_page, total)


@bp.get("/reports")
@roles_required("admin")
def reports():
    from datetime import datetime, timedelta
    try:
        start = datetime.strptime(request.args["from"], "%Y-%m-%d") if request.args.get("from") else datetime.utcnow() - timedelta(days=30)
        end = (datetime.strptime(request.args["to"], "%Y-%m-%d") if request.args.get("to") else datetime.utcnow()) + timedelta(days=1)
    except ValueError:
        raise ApiError("Dates must be YYYY-MM-DD.", 400, "bad_request")
    rows = Ticket.query.filter(Ticket.created_at >= start, Ticket.created_at < end).order_by(Ticket.created_at.desc()).all()
    if request.args.get("format") == "csv":
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["ticket_number", "subject", "customer", "agent", "category", "priority", "status", "created_at", "resolved_at", "sla_status"])
        for t in rows:
            w.writerow([t.ticket_number, t.subject, t.customer.email, t.agent.email if t.agent else "", t.category.category_name,
                        t.priority, t.status, t.created_at.isoformat(), t.resolved_at.isoformat() if t.resolved_at else "",
                        sla_service.compute_status(t.sla) if t.sla else ""])
        return Response(buf.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=tickets_report.csv"})
    by = lambda f: {}
    summary = {"total": len(rows)}
    for key, fn in (("by_status", lambda t: t.status), ("by_priority", lambda t: t.priority), ("by_category", lambda t: t.category.category_name)):
        d = {}
        for t in rows:
            d[fn(t)] = d.get(fn(t), 0) + 1
        summary[key] = d
    return ok({"from": start.date().isoformat(), "to": (end - timedelta(days=1)).date().isoformat(), "summary": summary,
               "agent_performance": analytics_service.agent_performance(), "sla": analytics_service.sla_summary(),
               "tickets": [t.to_dict() for t in rows[:200]]})


@bp.get("/audit-logs")
@roles_required("admin")
def audit_logs():
    page, per_page = page_params(20)
    q = AuditLog.query
    if request.args.get("action"):
        q = q.filter(AuditLog.action == request.args["action"])
    if request.args.get("user_id", "").isdigit():
        q = q.filter(AuditLog.user_id == int(request.args["user_id"]))
    total = q.count()
    items = q.order_by(AuditLog.created_at.desc(), AuditLog.log_id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return paginated([i.to_dict() for i in items], page, per_page, total)


@bp.get("/settings")
@roles_required("admin")
def get_settings():
    return ok(sla_service.get_settings())


@bp.put("/settings")
@roles_required("admin")
def put_settings():
    d = json_body()
    allowed = set(sla_service.DEFAULT_SETTINGS)
    errors, clean = {}, {}
    for k, v in d.items():
        if k not in allowed:
            errors[k] = "Unknown setting."
            continue
        try:
            n = float(v)
            if n <= 0 or n > 10000:
                raise ValueError
            clean[k] = v
        except (TypeError, ValueError):
            errors[k] = "Must be a positive number."
    raise_if(errors)
    sla_service.update_settings(clean)
    audit_service.audit(current_user(), "settings_updated", "settings", None, ", ".join(clean))
    db.session.commit()
    return ok(sla_service.get_settings(), "Settings saved.")
