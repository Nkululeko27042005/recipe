from app.extensions import db


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.String(50), default="")  # "2", "1/2"
    unit = db.Column(db.String(50), default="")       # "cups", "g", "tbsp"
    weight = db.Column(db.String(50), default="")     # optional extra
    notes = db.Column(db.String(255), default="")
    position = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "weight": self.weight,
            "notes": self.notes,
            "position": self.position,
        }