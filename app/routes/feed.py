from datetime import datetime
from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from app.services.feed_service import FeedService

feed_bp = Blueprint("feed", __name__)


@feed_bp.get("/")
def dashboard():
    """Renders the main dashboard (uses feed service)."""
    # Sections available to everyone
    common = {
        "feed":                         FeedService.main_feed(),
        "top_liked":                    FeedService.top_liked(),
        "most_famous_recipe":           FeedService.most_famous_recipe(),
        "most_interacted_this_month":   FeedService.most_interacted_recipe_this_month(),
        "most_saved":                   FeedService.most_saved(),
        "fresh_this_week":              FeedService.fresh_this_week(),
        "rising_users":                 FeedService.rising_users(),
        "top_cooks_this_month":         FeedService.top_cooks_this_month(),
        "now_month":                    datetime.utcnow().strftime("%B %Y"),
    }

    if current_user.is_authenticated:
        data = {
            **common,
            "my_recipes":  FeedService.my_recipes(current_user),
            "saved":       FeedService.saved_recipes(current_user),
            "recommended": FeedService.recommended_for(current_user),
        }
    else:
        data = common

    return render_template("dashboard.html", **data)


# ── JSON API endpoints ────────────────────────────────────────────────── #

@feed_bp.get("/api/feed")
def api_feed():
    uid = current_user.id if current_user.is_authenticated else None
    return jsonify([r.to_dict(current_user_id=uid) for r in FeedService.main_feed()])


@feed_bp.get("/api/top-liked")
def api_top_liked():
    uid = current_user.id if current_user.is_authenticated else None
    return jsonify([r.to_dict(current_user_id=uid) for r in FeedService.top_liked()])


@feed_bp.get("/api/most-saved")
def api_most_saved():
    uid = current_user.id if current_user.is_authenticated else None
    return jsonify([r.to_dict(current_user_id=uid) for r in FeedService.most_saved()])


@feed_bp.get("/api/fresh-this-week")
def api_fresh_this_week():
    uid = current_user.id if current_user.is_authenticated else None
    return jsonify([r.to_dict(current_user_id=uid) for r in FeedService.fresh_this_week()])


@feed_bp.get("/api/rising-users")
def api_rising_users():
    return jsonify([u.to_dict(include_stats=True) for u in FeedService.rising_users()])


@feed_bp.get("/api/top-cooks-this-month")
def api_top_cooks_this_month():
    return jsonify([
        {**u.to_dict(include_stats=True), "score": score}
        for u, score in FeedService.top_cooks_this_month()
    ])


@feed_bp.get("/api/recommended")
def api_recommended():
    if not current_user.is_authenticated:
        return jsonify([])
    return jsonify([r.to_dict(current_user_id=current_user.id)
                    for r in FeedService.recommended_for(current_user)])


@feed_bp.get("/api/my-recipes")
def api_my_recipes():
    if not current_user.is_authenticated:
        return jsonify([])
    return jsonify([r.to_dict(current_user_id=current_user.id)
                    for r in FeedService.my_recipes(current_user)])


@feed_bp.get("/api/saved")
def api_saved():
    if not current_user.is_authenticated:
        return jsonify([])
    return jsonify([r.to_dict(current_user_id=current_user.id)
                    for r in FeedService.saved_recipes(current_user)])