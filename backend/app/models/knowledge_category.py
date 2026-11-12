from datetime import datetime

from ..extensions import db


class KnowledgeCategory(db.Model):
    __tablename__ = "knowledge_categories"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    articles = db.relationship("KnowledgeArticle", backref="category")

    def to_dict(self):
        return {"category_id": self.category_id, "category_name": self.category_name, "description": self.description}
