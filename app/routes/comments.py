from flask import Blueprint, request
from flask_login import current_user
from app.models import Recipe, Comment
from app.services.comment_service import CommentService
from app.utils.responses import ok, created, error
from app.utils.decorators import login_required_json

comments_bp = Blueprint("comments", __name__)


@comments_bp.get("/recipe/<int:recipe_id>")
def list_comments(recipe_id):
    Recipe.query.get_or_404(recipe_id)
    comments = CommentService.list_for_recipe(recipe_id)
    return ok([c.to_dict(include_replies=True) for c in comments])


@comments_bp.post("/recipe/<int:recipe_id>")
@login_required_json
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json(silent=True) or request.form
    body = (data.get("body") or "").strip()
    if not body:
        return error("body is required", 422)

    try:
        comment = CommentService.add_comment(
            current_user, recipe, body, parent_id=data.get("parent_id")
        )
    except ValueError as e:
        return error(str(e), 400)

    return created(comment.to_dict(), "Comment added")


@comments_bp.delete("/<int:comment_id>")
@login_required_json
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    try:
        CommentService.delete_comment(comment, current_user)
    except PermissionError as e:
        return error(str(e), 403)
    return ok(message="Deleted")