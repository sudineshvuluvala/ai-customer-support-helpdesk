from flask import Blueprint, request

from ..extensions import db
from ..models import KnowledgeArticle, KnowledgeCategory
from ..services import audit_service, knowledge_service as ks
from ..utils.error_handlers import ApiError, ok, paginated
from ..utils.permissions import current_user, login_required, roles_required
from ..utils.validators import get_str, json_body, page_params, raise_if

bp = Blueprint("knowledge", __name__, url_prefix="/api/v1/knowledge")


@bp.get("/categories")
@login_required
def list_categories():
    return ok([c.to_dict() for c in KnowledgeCategory.query.order_by(KnowledgeCategory.category_name).all()])


@bp.post("/categories")
@roles_required("admin")
def create_category():
    d, errors = json_body(), {}
    name = get_str(d, "category_name", max_len=100, errors=errors)
    desc = get_str(d, "description", required=False, max_len=255, errors=errors)
    raise_if(errors)
    if KnowledgeCategory.query.filter(KnowledgeCategory.category_name.ilike(name)).first():
        raise ApiError("Category already exists.", 409, "duplicate")
    c = KnowledgeCategory(category_name=name, description=desc)
    db.session.add(c)
    db.session.commit()
    return ok(c.to_dict(), "Knowledge category created.", 201)


@bp.put("/categories/<int:cid>")
@roles_required("admin")
def update_category(cid):
    c = db.session.get(KnowledgeCategory, cid)
    if not c:
        raise ApiError("Category not found.", 404, "not_found")
    d, errors = json_body(), {}
    name = get_str(d, "category_name", max_len=100, errors=errors)
    desc = get_str(d, "description", required=False, max_len=255, errors=errors)
    raise_if(errors)
    c.category_name, c.description = name, desc
    db.session.commit()
    return ok(c.to_dict(), "Knowledge category updated.")


@bp.delete("/categories/<int:cid>")
@roles_required("admin")
def delete_category(cid):
    c = db.session.get(KnowledgeCategory, cid)
    if not c:
        raise ApiError("Category not found.", 404, "not_found")
    if c.articles:
        raise ApiError("Category contains articles. Move or delete them first.", 409, "in_use")
    db.session.delete(c)
    db.session.commit()
    return ok(None, "Knowledge category deleted.")


@bp.get("/articles")
@login_required
def list_articles():
    page, per_page = page_params()
    items, total = ks.list_articles(current_user(), request.args, page, per_page)
    return paginated([a.to_dict(full=False) for a in items], page, per_page, total)


@bp.get("/articles/<int:aid>")
@login_required
def get_article(aid):
    a = ks.get_article(aid, current_user())
    d = a.to_dict()
    d["related"] = [r.to_dict(full=False) for r in ks.related_articles(a)]
    return ok(d)


def _article_fields(d):
    errors = {}
    title = get_str(d, "title", max_len=200, min_len=3, errors=errors)
    content = get_str(d, "content", max_len=50000, min_len=10, errors=errors)
    cid = d.get("category_id")
    if not (str(cid).isdigit() and db.session.get(KnowledgeCategory, int(cid))):
        errors["category_id"] = "Select a valid category."
    status = d.get("status", "draft")
    if status not in ks.STATUSES:
        errors["status"] = "Must be draft, published or archived."
    raise_if(errors)
    return title, content, int(cid), status


@bp.post("/articles")
@roles_required("admin")
def create_article():
    title, content, cid, status = _article_fields(json_body())
    a = KnowledgeArticle(title=title, content=content, category_id=cid, status=status, created_by=current_user().user_id)
    db.session.add(a)
    db.session.flush()
    audit_service.audit(current_user(), "article_created", "article", a.article_id, title)
    db.session.commit()
    return ok(a.to_dict(), "Article created.", 201)


@bp.put("/articles/<int:aid>")
@roles_required("admin")
def update_article(aid):
    a = db.session.get(KnowledgeArticle, aid)
    if not a:
        raise ApiError("Article not found.", 404, "not_found")
    d = json_body()
    d.setdefault("status", a.status)
    a.title, a.content, a.category_id, a.status = _article_fields(d)
    audit_service.audit(current_user(), "article_updated", "article", aid, f"{a.title} [{a.status}]")
    db.session.commit()
    return ok(a.to_dict(), "Article updated.")


@bp.delete("/articles/<int:aid>")
@roles_required("admin")
def delete_article(aid):
    a = db.session.get(KnowledgeArticle, aid)
    if not a:
        raise ApiError("Article not found.", 404, "not_found")
    audit_service.audit(current_user(), "article_deleted", "article", aid, a.title)
    db.session.delete(a)
    db.session.commit()
    return ok(None, "Article deleted.")
