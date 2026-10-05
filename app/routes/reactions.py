from flask import Blueprint, request
from flask_login import current_user
from app.models import Recipe
from app.services.reaction_service import ReactionService
from app.utils.responses import ok, error
from app.utils.decorators import login_required_json

reactions_bp = Blueprint("reactions", __name__)


def _apply(recipe_id, value):
    recipe = Recipe.query.get_or_404(recipe_id)
    ReactionService.set_reaction(current_user, recipe, value)
    return ok({
        "likes": recipe.likes_count,
        "dislikes": recipe.dislikes_count,
        "my_reaction": value,
    }, "Reaction updated")


@reactions_bp.post("/recipe/<int:recipe_id>")
@login_required_json
def react(recipe_id):
    data = request.get_json(silent=True) or request.form
    try:
        value = int(data.get("value", 0))
    except (TypeError, ValueError):
        return error("value must be 1 (like), -1 (dislike) or 0 (clear)", 422)
    if value not in (-1, 0, 1):
        return error("value must be 1, -1 or 0", 422)
    return _apply(recipe_id, value)


# README-friendly aliases
@reactions_bp.post("/<int:recipe_id>/like")
@login_required_json
def like(recipe_id):
    return _apply(recipe_id, 1)


@reactions_bp.post("/<int:recipe_id>/dislike")
@login_required_json
def dislike(recipe_id):
    return _apply(recipe_id, -1)


@reactions_bp.delete("/<int:recipe_id>")
@login_required_json
def clear(recipe_id):
    return _apply(recipe_id, 0)