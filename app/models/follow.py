from datetime import datetime
from app.extensions import db


class Follow(db.Model):
    __tablename__ = "follows"
    __table_args__ = (
        db.UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair"),
    )

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"follower_id": self.follower_id, "followed_id": self.followed_id}