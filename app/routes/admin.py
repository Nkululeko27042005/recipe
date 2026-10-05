from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import User, Recipe, Comment
from app.utils.decorators import admin_required
from app.services.recipe_service import RecipeService

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/")
@admin_required
def dashboard():
    stats = {
        "users":    User.query.count(),
        "recipes":  Recipe.query.count(),
        "comments": Comment.query.count(),
    }
    recent_recipes = Recipe.query.order_by(Recipe.created_at.desc()).limit(10).all()
    recent_users   = User.query.order_by(User.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html",
                           stats=stats,
                           recent_recipes=recent_recipes,
                           recent_users=recent_users)


@admin_bp.get("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.post("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"Deleted user {user.username}", "success")
    return redirect(url_for("admin.users"))


@admin_bp.get("/recipes")
@admin_required
def recipes():
    all_recipes = Recipe.query.order_by(Recipe.created_at.desc()).all()
    return render_template("admin/recipes.html", recipes=all_recipes)


@admin_bp.post("/recipes/<int:recipe_id>/delete")
@admin_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    RecipeService.delete_recipe(recipe)
    flash("Recipe deleted.", "success")
    return redirect(url_for("admin.recipes"))