from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    kind = db.Column(db.String(30), nullable=False)   # like / comment / follow / reply
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="notifications")
    actor = db.relationship("User", foreign_keys=[actor_id], lazy="joined")
    recipe = db.relationship("Recipe", back_populates="notifications", lazy="joined")
    comment = db.relationship("Comment", back_populates="notifications", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "kind": self.kind,
            "actor": self.actor.to_dict() if self.actor else None,
            "recipe_id": self.recipe_id,
            "recipe_title": self.recipe.title if self.recipe else None,
            "comment_id": self.comment_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }