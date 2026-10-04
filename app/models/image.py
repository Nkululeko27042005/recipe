from app.extensions import db


class RecipeImage(db.Model):
    __tablename__ = "recipe_images"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": f"/static/uploads/{self.filename}",
            "is_primary": self.is_primary,
        }