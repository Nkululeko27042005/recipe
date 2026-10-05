from datetime import datetime
from app.extensions import db

# many-to-many for saved recipes
saved_recipes = db.Table(
    "saved_recipes",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("recipe_id", db.Integer, db.ForeignKey("recipes.id"), primary_key=True),
    db.Column("saved_at", db.DateTime, default=datetime.utcnow),
)


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(80), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    ingredients = db.relationship("Ingredient", backref="recipe", lazy="select",
                                  cascade="all, delete-orphan", order_by="Ingredient.position")
    steps = db.relationship("Step", backref="recipe", lazy="select",
                            cascade="all, delete-orphan", order_by="Step.position")
    images = db.relationship("RecipeImage", backref="recipe", lazy="select",
                             cascade="all, delete-orphan")
    video = db.relationship("RecipeVideo", backref="recipe", uselist=False,
                            cascade="all, delete-orphan")
    comments = db.relationship("Comment", backref="recipe", lazy="dynamic",
                               cascade="all, delete-orphan")
    reactions = db.relationship("Reaction", backref="recipe", lazy="dynamic",
                                cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="recipe", cascade="all, delete-orphan")
    savers = db.relationship("User", secondary=saved_recipes, lazy="dynamic",
                             backref=db.backref("saved_recipes", lazy="dynamic"))

    @property
    def likes_count(self):
        return self.reactions.filter_by(value=1).count()

    @property
    def dislikes_count(self):
        return self.reactions.filter_by(value=-1).count()

    def to_dict(self, detailed=False, current_user_id=None):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "author": self.author.to_dict() if self.author else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "likes": self.likes_count,
            "dislikes": self.dislikes_count,
            "comments_count": self.comments.count(),
            "images": [img.to_dict() for img in self.images],
            "video": self.video.to_dict() if self.video else None,
        }
        if current_user_id:
            r = self.reactions.filter_by(user_id=current_user_id).first()
            data["my_reaction"] = r.value if r else 0
            data["is_saved"] = self.savers.filter_by(id=current_user_id).first() is not None
        if detailed:
            data["ingredients"] = [i.to_dict() for i in self.ingredients]
            data["steps"] = [s.to_dict() for s in self.steps]
        return data