from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, default="")
    avatar = db.Column(db.String(255), default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    recipes = db.relationship("Recipe", backref="author", lazy="dynamic",
                              cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="author", lazy="dynamic",
                               cascade="all, delete-orphan")
    reactions = db.relationship("Reaction", backref="user", lazy="dynamic",
                                cascade="all, delete-orphan")
    preference = db.relationship("UserPreference", backref="user", uselist=False,
                                 cascade="all, delete-orphan")

    # follow relationships
    following = db.relationship(
        "Follow", foreign_keys="Follow.follower_id",
        backref="follower", lazy="dynamic", cascade="all, delete-orphan"
    )
    followers = db.relationship(
        "Follow", foreign_keys="Follow.followed_id",
        backref="followed", lazy="dynamic", cascade="all, delete-orphan"
    )

    def set_password(self, raw):
        self.password_hash = bcrypt.generate_password_hash(raw).decode()

    def check_password(self, raw):
        return bcrypt.check_password_hash(self.password_hash, raw)

    def to_dict(self, include_stats=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "bio": self.bio,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat(),
        }
        if include_stats:
            data["followers_count"] = self.followers.count()
            data["following_count"] = self.following.count()
            data["recipes_count"] = self.recipes.count()
        return data


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    # store comma-separated categories/preferences (or migrate to JSON if using PG)
    categories = db.Column(db.Text, default="")
    dietary = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_categories(self):
        return [c.strip() for c in (self.categories or "").split(",") if c.strip()]

    def get_dietary(self):
        return [d.strip() for d in (self.dietary or "").split(",") if d.strip()]

    def to_dict(self):
        return {
            "categories": self.get_categories(),
            "dietary": self.get_dietary(),
        }


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))