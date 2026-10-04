from flask import Blueprint, request
from app.models import User, Recipe
from flask_login import current_user
from app.services.user_service import UserService
from app.utils.responses import ok, error
from app.utils.decorators import login_required_json

users_bp = Blueprint("users", __name__)


@users_bp.get("/<int:user_id>")
def get_user(user_id):
    user = UserService.get_user(user_id)
    return ok(user.to_dict(include_stats=True))


@users_bp.put("/me")
@login_required_json
def update_me():
    data = request.get_json(silent=True) or request.form
    avatar_file = request.files.get("avatar")
    remove_avatar = data.get("remove_avatar") == "1"

    # Handle avatar file upload
    avatar_filename = None
    if avatar_file and avatar_file.filename:
        from app.utils.file_handler import save_file
        try:
            avatar_filename = save_file(avatar_file, kind="image")
        except ValueError as e:
            return error(str(e), 422)
    elif remove_avatar:
        avatar_filename = ""  # empty string = clear avatar

    user = UserService.update_user(
        current_user,
        bio=data.get("bio"),
        avatar=avatar_filename,
    )
    return ok(user.to_dict(include_stats=True), "Updated")


@users_bp.put("/me/preferences")
@login_required_json
def update_preferences():
    data = request.get_json(silent=True) or {}
    prefs = UserService.update_preferences(
        current_user,
        categories=data.get("categories"),
        dietary=data.get("dietary"),
    )
    return ok(prefs.to_dict(), "Preferences updated")


@users_bp.get("/me/preferences")
@login_required_json
def get_preferences():
    prefs = current_user.preference
    return ok(prefs.to_dict() if prefs else {"categories": [], "dietary": []})


@users_bp.get("/search")
def search_users():
    q = request.args.get("q", "").strip()
    if not q:
        return ok([])
    results = UserService.search(q)
    return ok([u.to_dict(include_stats=True) for u in results])

from flask import render_template
from flask_login import login_required
from app.services.follow_service import FollowService

@users_bp.get("/u/<username>")
def profile_page(username):
    user = User.query.filter_by(username=username).first_or_404()
    recipes = (Recipe.query.filter_by(user_id=user.id)
               .order_by(Recipe.created_at.desc()).all())
    is_following = False
    if current_user.is_authenticated and current_user.id != user.id:
        is_following = FollowService.is_following(current_user, user)
    return render_template("profile.html",
                           profile_user=user,
                           recipes=recipes,
                           is_following=is_following)


@users_bp.get("/settings")
@login_required
def settings_page():
    prefs = current_user.preference
    if prefs is None:
        from app.models import UserPreference
        prefs = UserPreference(user_id=current_user.id)
    return render_template("settings.html", prefs=prefs)