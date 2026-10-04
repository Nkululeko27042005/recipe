import json
from flask import Blueprint, request, abort, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.services.comment_service import CommentService
from app.services.recipe_service import RecipeService
from app.models import Recipe
from app.utils.responses import ok, created, error
from app.utils.decorators import login_required_json

recipes_bp = Blueprint("recipes", __name__)


def _parse_json_field(field):
    """Handles ingredients/steps arriving as JSON strings via multipart."""
    if not field:
        return []
    if isinstance(field, list):
        return field
    try:
        return json.loads(field)
    except (TypeError, ValueError):
        return []


@recipes_bp.get("/")
def list_recipes():
    category = request.args.get("category")
    search = request.args.get("q")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    recipes = RecipeService.list_recipes(category, search, limit, offset)
    uid = current_user.id if current_user.is_authenticated else None
    return ok([r.to_dict(current_user_id=uid) for r in recipes])


@recipes_bp.get("/<int:recipe_id>")
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    uid = current_user.id if current_user.is_authenticated else None
    return ok(recipe.to_dict(detailed=True, current_user_id=uid))


@recipes_bp.post("/")
@login_required_json
def create_recipe():
    # supports both JSON and multipart form-data
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        data = {
            "title": request.form.get("title", "").strip(),
            "description": request.form.get("description", ""),
            "category": request.form.get("category", ""),
            "ingredients": _parse_json_field(request.form.get("ingredients")),
            "steps": _parse_json_field(request.form.get("steps")),
        }
        images = request.files.getlist("images")
        video = request.files.get("video")
    else:
        data = request.get_json(silent=True) or {}
        images = None
        video = None

    if not data.get("title"):
        return error("title is required", 422)

    recipe = RecipeService.create_recipe(current_user, data, images, video)
    return created(recipe.to_dict(detailed=True, current_user_id=current_user.id),
                   "Recipe created")


@recipes_bp.put("/<int:recipe_id>")
@login_required_json
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        return error("Not allowed", 403)

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        data = {}
        for f in ("title", "description", "category"):
            if request.form.get(f) is not None:
                data[f] = request.form.get(f)
        if request.form.get("ingredients"):
            data["ingredients"] = _parse_json_field(request.form.get("ingredients"))
        if request.form.get("steps"):
            data["steps"] = _parse_json_field(request.form.get("steps"))
        new_images = request.files.getlist("images") or None
        new_video = request.files.get("video")
        remove_ids = _parse_json_field(request.form.get("remove_image_ids"))
        remove_ids = [int(i) for i in remove_ids]
    else:
        data = request.get_json(silent=True) or {}
        new_images = new_video = None
        remove_ids = None

    recipe = RecipeService.update_recipe(recipe, data, new_images, new_video, remove_ids)
    return ok(recipe.to_dict(detailed=True, current_user_id=current_user.id), "Updated")


@recipes_bp.delete("/<int:recipe_id>")
@login_required_json
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        return error("Not allowed", 403)
    RecipeService.delete_recipe(recipe)
    return ok(message="Deleted")


@recipes_bp.post("/<int:recipe_id>/save")
@login_required_json
def save_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    RecipeService.save_for_user(current_user, recipe)
    return ok({"id": recipe.id, "is_saved": True}, "Saved")


@recipes_bp.delete("/<int:recipe_id>/save")
@login_required_json
def unsave_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    RecipeService.unsave_for_user(current_user, recipe)
    return ok({"id": recipe.id, "is_saved": False}, "Unsaved")

@recipes_bp.get("/page")
def list_recipes_page():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip() or None
    page = max(int(request.args.get("page", 1)), 1)
    per_page = 12

    base = Recipe.query
    if q:        base = base.filter(Recipe.title.ilike(f"%{q}%"))
    if category: base = base.filter(Recipe.category.ilike(category))

    total = base.count()
    recipes = (base.order_by(Recipe.created_at.desc())
               .limit(per_page).offset((page - 1) * per_page).all())
    total_pages = (total + per_page - 1) // per_page

    return render_template("recipe_list.html",
                           recipes=recipes, q=q, category=category,
                           page=page, total_pages=total_pages)


@recipes_bp.get("/<int:recipe_id>/view")
def recipe_page(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    uid = current_user.id if current_user.is_authenticated else None
    my_reaction = 0
    is_saved = False
    if uid:
        r = recipe.reactions.filter_by(user_id=uid).first()
        my_reaction = r.value if r else 0
        is_saved = recipe.savers.filter_by(id=uid).first() is not None
    comments = CommentService.list_for_recipe(recipe.id)
    return render_template("recipe_detail.html",
                           recipe=recipe, comments=comments,
                           my_reaction=my_reaction, is_saved=is_saved)


@recipes_bp.get("/new")
@login_required
def new_recipe_page():
    return render_template("recipe_form.html", recipe=None)


@recipes_bp.get("/<int:recipe_id>/edit")
@login_required
def edit_recipe_page(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != current_user.id:
        abort(403)
    return render_template("recipe_form.html", recipe=recipe)