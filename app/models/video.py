from app.extensions import db


class RecipeVideo(db.Model):
    __tablename__ = "recipe_videos"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "url": f"/static/uploads/{self.filename}",
        }