from datetime import datetime
from app.extensions import db


class Reaction(db.Model):
    __tablename__ = "reactions"
    __table_args__ = (
        db.UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe_reaction"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    value = db.Column(db.Integer, nullable=False)  # 1 = like, -1 = dislike
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "value": self.value, "user_id": self.user_id,
                "recipe_id": self.recipe_id}