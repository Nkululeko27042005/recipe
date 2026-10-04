from flask import Blueprint
from flask_login import current_user
from app.models import User
from app.services.follow_service import FollowService
from app.utils.responses import ok, error
from app.utils.decorators import login_required_json

follows_bp = Blueprint("follows", __name__)


@follows_bp.post("/<int:user_id>")
@login_required_json
def follow(user_id):
    target = User.query.get_or_404(user_id)
    try:
        FollowService.follow(current_user, target)
    except ValueError as e:
        return error(str(e), 400)
    return ok(message="Followed")


@follows_bp.delete("/<int:user_id>")
@login_required_json
def unfollow(user_id):
    target = User.query.get_or_404(user_id)
    FollowService.unfollow(current_user, target)
    return ok(message="Unfollowed")


@follows_bp.get("/<int:user_id>/followers")
def followers(user_id):
    user = User.query.get_or_404(user_id)
    return ok([u.to_dict(include_stats=True) for u in FollowService.followers(user)])


@follows_bp.get("/<int:user_id>/following")
def following(user_id):
    user = User.query.get_or_404(user_id)
    return ok([u.to_dict(include_stats=True) for u in FollowService.following(user)])