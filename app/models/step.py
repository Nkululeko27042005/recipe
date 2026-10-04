from app.extensions import db


class Step(db.Model):
    __tablename__ = "steps"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=1)
    instruction = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "instruction": self.instruction,
        }