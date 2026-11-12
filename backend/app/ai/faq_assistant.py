import re

from ..services.knowledge_service import published_articles
from . import ai_config, knowledge_search as ks, prompt_templates as pt, safety_checks as sc

RELIABLE_THRESHOLD = 0.5

NO_ANSWER_TEXT = ("I couldn't find a reliable answer in our knowledge base for that question. "
                  "I don't want to guess about policies or account details - please create a support ticket and an agent will help you.")


def answer(question, history=None):
    q = sc.validate_question(question)
    if not q:
        return None
    # fold the previous customer turns in so follow-up questions retrieve well
    prior = [h.get("content", "") for h in (history or [])[-4:] if isinstance(h, dict) and h.get("role") == "user"]
    retrieval_query = re.sub(r"\[(email|number|phone)\]", " ", sc.sanitize_for_provider(" ".join(prior[-1:] + [q])))
    hits = ks.search(published_articles(), retrieval_query, limit=3)
    reliable = [h for h in hits if h[1] >= RELIABLE_THRESHOLD]
    cards = [ks.article_card(a, s, q) for a, s in hits]
    if not reliable:
        return {"answer": NO_ANSWER_TEXT, "articles": cards[:3], "reliable": False, "suggest_ticket": True, "source": "none",
                "ai": ai_config.status()}
    top = reliable[:2]
    source = "knowledge-base"
    text = None
    if ai_config.is_configured() and not sc.looks_like_injection(q):
        context = "\n\n".join(f"[{a.title}]\n{a.content[:1200]}" for a, _ in top)
        hist = "\n".join(f"{h.get('role', 'user')}: {sc.sanitize_for_provider(str(h.get('content', '')))}"
                         for h in (history or [])[-4:] if isinstance(h, dict))
        try:
            raw = ai_config.call_llm(pt.FAQ_SYSTEM, pt.FAQ_USER.format(context=context, history=hist, question=sc.sanitize_for_provider(q)))
            text = sc.validate_output(raw)
            if text:
                source = "llm"
        except ai_config.AIUnavailable:
            text = None
    if not text:  # extractive fallback straight from the article text
        text = ks.best_snippet(top[0][0], q)
        text = f"Based on our article \"{top[0][0].title}\": {text}"
    return {"answer": text, "articles": cards, "reliable": True, "suggest_ticket": False, "source": source, "ai": ai_config.status()}
