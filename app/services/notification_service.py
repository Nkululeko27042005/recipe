from app.extensions import db
from app.models import Notification


class NotificationService:

    @staticmethod
    def create(user_id, kind, actor=None, recipe=None, comment=None):
        """Don't notify if the actor is the target."""
        if actor and actor.id == user_id:
            return None
        n = Notification(
            user_id=user_id,
            actor_id=actor.id if actor else None,
            kind=kind,
            recipe_id=recipe.id if recipe else None,
            comment_id=comment.id if comment else None,
        )
        db.session.add(n)
        db.session.commit()
        return n

    @staticmethod
    def list_for(user, limit=50):
        return (Notification.query
                .filter_by(user_id=user.id)
                .order_by(Notification.created_at.desc())
                .limit(limit).all())

    @staticmethod
    def unread_count(user):
        return (Notification.query
                .filter_by(user_id=user.id, is_read=False)
                .count())

    @staticmethod
    def mark_all_read(user):
        (Notification.query
         .filter_by(user_id=user.id, is_read=False)
         .update({"is_read": True}))
        db.session.commit()