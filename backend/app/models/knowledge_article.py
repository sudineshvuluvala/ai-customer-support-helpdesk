from datetime import datetime

from ..extensions import db
from .ticket import iso


class KnowledgeArticle(db.Model):
    __tablename__ = "knowledge_articles"
    article_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("knowledge_categories.category_id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum("draft", "published", "archived", name="article_status"), nullable=False, default="draft", index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self, full=True):
        d = {
            "article_id": self.article_id,
            "title": self.title,
            "category": self.category.to_dict() if self.category else None,
            "status": self.status,
            "summary": (self.content[:180] + "...") if len(self.content) > 180 else self.content,
            "created_at": iso(self.created_at),
            "updated_at": iso(self.updated_at),
        }
        if full:
            d["content"] = self.content
        return d
