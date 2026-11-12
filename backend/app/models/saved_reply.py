from datetime import datetime

from ..extensions import db


class SavedReply(db.Model):
    __tablename__ = "saved_replies"
    reply_id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    reply_content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"reply_id": self.reply_id, "title": self.title, "reply_content": self.reply_content}
