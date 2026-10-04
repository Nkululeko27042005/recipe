from app.extensions import db
from app.models import Reaction


class ReactionService:

    @staticmethod
    def set_reaction(user, recipe, value):
        """value: 1 = like, -1 = dislike, 0 = clear"""
        existing = Reaction.query.filter_by(user_id=user.id, recipe_id=recipe.id).first()

        if value == 0:
            if existing:
                db.session.delete(existing)
                db.session.commit()
            return None

        if existing:
            existing.value = value
        else:
            existing = Reaction(user_id=user.id, recipe_id=recipe.id, value=value)
            db.session.add(existing)

        db.session.commit()
        return existing