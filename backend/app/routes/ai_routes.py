from flask import Blueprint, request

from ..ai import ai_config, faq_assistant, knowledge_search as kse, response_generator, safety_checks as sc, ticket_classifier
from ..extensions import limiter
from ..services import conversation_service as cs, ticket_service as ts
from ..services.knowledge_service import published_articles
from ..utils.error_handlers import ApiError, ok
from ..utils.permissions import current_user, login_required, roles_required
from ..utils.validators import json_body

bp = Blueprint("ai", __name__, url_prefix="/api/v1/ai")


@bp.get("/status")
@login_required
def status():
    return ok(ai_config.status())


@bp.post("/chat")
@login_required
@limiter.limit("30 per minute")
def chat():
    d = json_body()
    result = faq_assistant.answer(d.get("message"), d.get("history") if isinstance(d.get("history"), list) else [])
    if result is None:
        raise ApiError("Please enter a question.", 422, "validation_error", {"message": "This field is required."})
    return ok(result)


@bp.post("/classify-ticket")
@login_required
@limiter.limit("30 per minute")
def classify():
    d = json_body()
    subject, desc = sc.validate_question(d.get("subject")), sc.validate_question(d.get("description"))
    if not subject or not desc:
        raise ApiError("Subject and description are required.", 422, "validation_error")
    return ok(ticket_classifier.classify(subject, desc))


@bp.post("/suggest-reply")
@roles_required("agent", "admin")
@limiter.limit("20 per minute")
def suggest_reply():
    d = json_body()
    tid = d.get("ticket_id")
    if not str(tid).isdigit():
        raise ApiError("ticket_id is required.", 422, "validation_error", {"ticket_id": "Required."})
    t = ts.get_ticket_for_user(int(tid), current_user())  # same ticket authorization as everything else
    return ok(response_generator.suggest(t, cs.list_messages(t, current_user())))


@bp.get("/search-knowledge")
@login_required
def search_knowledge():
    q = sc.validate_question(request.args.get("q"))
    if not q:
        raise ApiError("Query parameter q is required.", 422, "validation_error", {"q": "Required."})
    hits = kse.search(published_articles(), q, limit=int(request.args.get("limit", 5)) if request.args.get("limit", "5").isdigit() else 5)
    return ok([kse.article_card(a, s, q) for a, s in hits], ai=ai_config.status(), query=q)
