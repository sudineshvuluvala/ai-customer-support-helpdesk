from sqlalchemy import or_

from ..extensions import db
from ..models import KnowledgeArticle, KnowledgeCategory
from ..utils.error_handlers import ApiError
from ..utils.validators import like_escape

STATUSES = ("draft", "published", "archived")


def list_articles(user, args, page, per_page):
    q = KnowledgeArticle.query
    if user.role == "admin":
        if args.get("status") in STATUSES:
            q = q.filter_by(status=args["status"])
    else:
        q = q.filter_by(status="published")
    if args.get("category_id", "").isdigit():
        q = q.filter_by(category_id=int(args["category_id"]))
    term = (args.get("q") or "").strip()
    if term:
        like = f"%{like_escape(term)}%"
        q = q.filter(or_(KnowledgeArticle.title.like(like, escape="\\"), KnowledgeArticle.content.like(like, escape="\\")))
    total = q.count()
    items = q.order_by(KnowledgeArticle.updated_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_article(article_id, user):
    a = db.session.get(KnowledgeArticle, article_id)
    if not a or (user.role != "admin" and a.status != "published"):
        raise ApiError("Article not found.", 404, "not_found")
    return a


def related_articles(article, limit=3):
    return (KnowledgeArticle.query.filter(KnowledgeArticle.category_id == article.category_id,
                                          KnowledgeArticle.article_id != article.article_id,
                                          KnowledgeArticle.status == "published")
            .order_by(KnowledgeArticle.updated_at.desc()).limit(limit).all())


def published_articles():
    return KnowledgeArticle.query.filter_by(status="published").all()
