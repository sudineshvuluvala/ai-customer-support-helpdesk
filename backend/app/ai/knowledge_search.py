"""Natural-language retrieval over PUBLISHED knowledge articles (idf-weighted term coverage + BM25-style ranking).

Works with no external provider, so the helpdesk and the assistant keep working offline.
"""
import math
import re
from collections import Counter

STOP = set("""a an the and or but if is are was were be been being to of in on at for with from by as it its this that these
those i you he she we they me my our your their do does did can could should would will just how what why when where which
who whom not no yes please hi hello hey help need want get have has had am there about into than then so up out""".split())


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def tokenize(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+", (text or "").lower()) if w not in STOP and len(w) > 1]


def search(articles, query, limit=5):
    """Returns [(article, coverage 0..1)] sorted best first. Only articles matching at least one term."""
    q_terms = list(dict.fromkeys(tokenize(query)))
    if not q_terms or not articles:
        return []
    docs = []
    for a in articles:
        title_tokens = tokenize(a.title)
        body_tokens = tokenize(a.content)
        docs.append((a, Counter(title_tokens), Counter(body_tokens), len(title_tokens) + len(body_tokens) or 1))
    n = len(docs)
    avg_len = sum(d[3] for d in docs) / n
    df = {t: sum(1 for d in docs if d[1][t] or d[2][t]) for t in q_terms}
    idf = {t: math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) for t in q_terms}
    idf_total = sum(idf.values()) or 1
    results = []
    for a, tt, bt, ln in docs:
        covered, bm25 = 0.0, 0.0
        for t in q_terms:
            tf = tt[t] * 3 + bt[t]  # title hits count triple
            if tf:
                covered += idf[t]
                bm25 += idf[t] * (tf * 2.2) / (tf + 1.2 * (0.25 + 0.75 * ln / avg_len))
        if covered:
            results.append((a, covered / idf_total, bm25))
    results.sort(key=lambda r: (r[1], r[2]), reverse=True)
    return [(a, round(c, 3)) for a, c, _ in results[:limit]]


def best_snippet(article, query, max_sentences=3):
    terms = set(tokenize(query))
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", article.content) if s.strip()]
    scored = sorted(enumerate(sentences), key=lambda p: -len(terms & set(tokenize(p[1]))))
    picked = sorted(i for i, _ in scored[:max_sentences])
    return " ".join(sentences[i] for i in picked)[:600]


def article_card(article, score=None, query=None):
    d = {"article_id": article.article_id, "title": article.title,
         "category": article.category.category_name if article.category else None,
         "summary": best_snippet(article, query) if query else article.content[:180]}
    if score is not None:
        d["relevance"] = score
    return d
