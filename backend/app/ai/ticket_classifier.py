import json
import re

from ..models import PRIORITIES, TicketCategory
from . import ai_config, prompt_templates as pt, safety_checks as sc

CATEGORY_KEYWORDS = {
    "Login Problems": ["login", "log in", "sign in", "password", "reset", "locked", "2fa", "otp", "cannot access"],
    "Account Issues": ["account", "profile", "email change", "delete account", "username", "verification"],
    "Billing": ["bill", "invoice", "payment", "charge", "charged", "refund", "subscription", "price", "card"],
    "Technical Support": ["error", "bug", "crash", "not working", "slow", "timeout", "exception", "fails", "broken", "500"],
    "Product Issues": ["product", "defect", "damaged", "feature", "item", "device", "faulty"],
    "Service Requests": ["request", "install", "setup", "upgrade", "configure", "onboard", "new feature"],
    "General Enquiries": ["question", "information", "how do i", "enquiry", "inquiry", "hours", "contact"],
}
PRIORITY_KEYWORDS = {
    "critical": ["outage", "down for everyone", "data loss", "security breach", "hacked", "production down", "all users", "urgent critical"],
    "high": ["urgent", "asap", "immediately", "cannot", "can't", "unable", "blocked", "charged twice", "double charged", "crash"],
    "low": ["question", "suggestion", "feedback", "when possible", "no rush", "minor", "curious"],
}


def _heuristic(subject, description, categories):
    text = f"{subject} {description}".lower()
    best, best_score = None, 0
    names = {c.category_name: c for c in categories}
    for name, kws in CATEGORY_KEYWORDS.items():
        if name in names:
            score = sum(2 if k in subject.lower() else 1 for k in kws if k in text)
            if score > best_score:
                best, best_score = names[name], score
    other = names.get("Other") or names.get("General Enquiries") or (categories[0] if categories else None)
    cat = best or other
    priority = "medium"
    for p in ("critical", "high", "low"):
        if any(k in text for k in PRIORITY_KEYWORDS[p]):
            priority = p
            break
    conf = min(0.4 + 0.15 * best_score, 0.9) if best else 0.3
    return {"category_id": cat.category_id if cat else None, "category_name": cat.category_name if cat else None,
            "priority": priority, "issue_type": (best.category_name if best else "Unclassified"),
            "confidence": round(conf, 2), "source": "local-rules"}


def classify(subject, description):
    categories = TicketCategory.query.filter_by(is_active=True).all()
    result = _heuristic(subject, description, categories)
    if ai_config.is_configured() and categories and not sc.looks_like_injection(subject + description):
        try:
            raw = ai_config.call_llm(
                pt.CLASSIFY_SYSTEM.format(categories=", ".join(c.category_name for c in categories)),
                pt.CLASSIFY_USER.format(subject=sc.sanitize_for_provider(subject), description=sc.sanitize_for_provider(description)),
                json_mode=True)
            data = json.loads(re.search(r"\{.*\}", raw, re.S).group(0))
            cat = next((c for c in categories if c.category_name.lower() == str(data.get("category", "")).lower()), None)
            pr = str(data.get("priority", "")).lower()
            if cat and pr in PRIORITIES:  # validate model output against allowed values
                result.update({"category_id": cat.category_id, "category_name": cat.category_name, "priority": pr,
                               "issue_type": str(data.get("issue_type", cat.category_name))[:80], "confidence": 0.8, "source": "llm"})
        except Exception:
            pass  # keep the local-rules suggestion
    result["ai"] = ai_config.status()
    result["note"] = "This is a suggestion only. You can change it before submitting."
    return result
