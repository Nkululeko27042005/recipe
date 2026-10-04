from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]),
                              lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_replies=False):
        data = {
            "id": self.id,
            "body": self.body,
            "author": self.author.to_dict() if self.author else None,
            "created_at": self.created_at.isoformat(),
            "parent_id": self.parent_id,
        }
        if include_replies:
            data["replies"] = [r.to_dict() for r in self.replies]
        return data