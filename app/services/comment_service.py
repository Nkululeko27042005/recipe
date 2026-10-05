from app.extensions import db
from app.models import Comment
from app.services.notification_service import NotificationService


class CommentService:

    @staticmethod
    def add_comment(user, recipe, body, parent_id=None):
        parent = None
        if parent_id:
            parent = Comment.query.get(parent_id)
            if not parent or parent.recipe_id != recipe.id:
                raise ValueError("Invalid parent comment")

        comment = Comment(recipe_id=recipe.id, user_id=user.id,
                          body=body, parent_id=parent_id)
        db.session.add(comment)
        db.session.commit()

        # Notify recipe author (unless it's their own comment)
        NotificationService.create(
            user_id=recipe.user_id, kind="comment",
            actor=user, recipe=recipe, comment=comment,
        )
        # If it's a reply, also notify the parent commenter
        if parent and parent.user_id != user.id:
            NotificationService.create(
                user_id=parent.user_id, kind="reply",
                actor=user, recipe=recipe, comment=comment,
            )
        return comment

    @staticmethod
    def delete_comment(comment, user):
        if comment.user_id != user.id:
            raise PermissionError("Not allowed")
        db.session.delete(comment)
        db.session.commit()

    @staticmethod
    def list_for_recipe(recipe_id, top_level_only=True):
        q = Comment.query.filter_by(recipe_id=recipe_id)
        if top_level_only:
            q = q.filter(Comment.parent_id.is_(None))
        return q.order_by(Comment.created_at.desc()).all()