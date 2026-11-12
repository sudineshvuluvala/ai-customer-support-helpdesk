from ..services.knowledge_service import published_articles
from . import ai_config, knowledge_search as ks, prompt_templates as pt, safety_checks as sc


def suggest(ticket, messages):
    """Builds a DRAFT reply. It is never sent automatically - the agent must edit/approve it and post it
    through the normal message endpoint."""
    public = [m for m in messages if m.message_type == "public"]
    last_customer = next((m for m in reversed(public) if m.sender_id == ticket.customer_id), None)
    question = (last_customer.message_content if last_customer else ticket.description)
    query = f"{ticket.subject} {question}"
    hits = [h for h in ks.search(published_articles(), query, limit=3) if h[1] >= 0.4]
    cards = [ks.article_card(a, s, question) for a, s in hits]
    first = (ticket.customer.name or "there").split()[0]
    text, source = None, "template"
    if ai_config.is_configured() and not sc.looks_like_injection(question):
        convo = "\n".join(f"{'Customer' if m.sender_id == ticket.customer_id else 'Agent'}: {sc.sanitize_for_provider(m.message_content)}"
                          for m in public[-6:]) or f"Customer: {sc.sanitize_for_provider(ticket.description)}"
        context = "\n\n".join(f"[{a.title}]\n{a.content[:1000]}" for a, _ in hits) or "(no matching articles)"
        try:
            raw = ai_config.call_llm(pt.REPLY_SYSTEM, pt.REPLY_USER.format(
                context=context, subject=sc.sanitize_for_provider(ticket.subject), conversation=convo))
            text = sc.validate_output(raw)
            source = "llm" if text else source
        except ai_config.AIUnavailable:
            text = None
    if not text:
        if hits:
            snippet = ks.best_snippet(hits[0][0], question)
            text = (f"Hi {first},\n\nThank you for contacting us about \"{ticket.subject}\". "
                    f"Our knowledge base article \"{hits[0][0].title}\" may help: {snippet}\n\n"
                    "Please let us know if this resolves the issue or if you can share more details.\n\nKind regards")
        else:
            text = (f"Hi {first},\n\nThank you for contacting us about \"{ticket.subject}\". "
                    "I'm looking into this now. Could you share any extra details (what you expected, what happened, "
                    "and any error messages or screenshots)?\n\nKind regards")
    return {"suggestion": text, "articles": cards, "source": source, "requires_approval": True, "ai": ai_config.status()}
