from app.extensions import db
from app.models import Reaction
from app.services.notification_service import NotificationService


class ReactionService:

    @staticmethod
    def set_reaction(user, recipe, value):
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

        # Only notify on LIKE (not dislike, not clear)
        if value == 1:
            NotificationService.create(
                user_id=recipe.user_id, kind="like", actor=user, recipe=recipe
            )
        return existing