from datetime import datetime, timedelta

from ..extensions import db
from ..models import AppSetting, SLARecord

# hours: (first response, resolution)
DEFAULT_SLA = {
    "critical": (1, 4),
    "high": (4, 8),
    "medium": (8, 24),
    "low": (24, 72),
}
DEFAULT_SETTINGS = {"auto_close_days": "7"}
for _p, (_r, _s) in DEFAULT_SLA.items():
    DEFAULT_SETTINGS[f"sla_response_hours_{_p}"] = str(_r)
    DEFAULT_SETTINGS[f"sla_resolution_hours_{_p}"] = str(_s)


def get_settings():
    out = dict(DEFAULT_SETTINGS)
    for s in AppSetting.query.all():
        out[s.key] = s.value
    return out


def update_settings(values):
    for k, v in values.items():
        row = db.session.get(AppSetting, k)
        if row:
            row.value = str(v)
        else:
            db.session.add(AppSetting(key=k, value=str(v)))


def targets_for(priority):
    s = get_settings()
    dr, ds = DEFAULT_SLA[priority]
    try:
        return float(s.get(f"sla_response_hours_{priority}", dr)), float(s.get(f"sla_resolution_hours_{priority}", ds))
    except ValueError:
        return float(dr), float(ds)


def create_sla(ticket):
    resp_h, res_h = targets_for(ticket.priority)
    created = ticket.created_at or datetime.utcnow()
    sla = SLARecord(
        ticket=ticket,
        response_due_at=created + timedelta(hours=resp_h),
        resolution_due_at=created + timedelta(hours=res_h),
    )
    db.session.add(sla)
    return sla


def recompute_due_dates(ticket):
    if not ticket.sla:
        return create_sla(ticket)
    resp_h, res_h = targets_for(ticket.priority)
    ticket.sla.response_due_at = ticket.created_at + timedelta(hours=resp_h)
    ticket.sla.resolution_due_at = ticket.created_at + timedelta(hours=res_h)
    ticket.sla.sla_status = compute_status(ticket.sla)
    return ticket.sla


def compute_status(sla, now=None):
    now = now or datetime.utcnow()
    if sla.resolved_at:
        return "met" if sla.resolved_at <= sla.resolution_due_at else "breached"
    if not sla.first_response_at and now > sla.response_due_at:
        return "breached"
    if now > sla.resolution_due_at:
        return "breached"
    created = sla.ticket.created_at if sla.ticket is not None else sla.response_due_at
    total = (sla.resolution_due_at - created).total_seconds()
    remaining = (sla.resolution_due_at - now).total_seconds()
    if total > 0 and remaining < 0.25 * total:
        return "at_risk"
    return "on_track"


def mark_first_response(ticket, when=None):
    if ticket.sla and not ticket.sla.first_response_at:
        ticket.sla.first_response_at = when or datetime.utcnow()
        ticket.sla.sla_status = compute_status(ticket.sla)


def mark_resolved(ticket, when=None):
    if ticket.sla:
        ticket.sla.resolved_at = when or datetime.utcnow()
        ticket.sla.sla_status = compute_status(ticket.sla)


def reopen(ticket):
    if ticket.sla:
        ticket.sla.resolved_at = None
        ticket.sla.sla_status = compute_status(ticket.sla)


def is_overdue(ticket, now=None):
    now = now or datetime.utcnow()
    if ticket.status in ("resolved", "closed") or not ticket.sla:
        return False
    return now > ticket.sla.resolution_due_at or (not ticket.sla.first_response_at and now > ticket.sla.response_due_at)
