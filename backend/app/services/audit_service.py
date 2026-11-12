from ..extensions import db
from ..models import AuditLog


def audit(user, action, entity_type, entity_id=None, description=""):
    db.session.add(AuditLog(
        user_id=user.user_id if user else None, action=action, entity_type=entity_type,
        entity_id=entity_id, description=(description or "")[:500],
    ))
