from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required
from app.services.notification_service import NotificationService
from app.utils.responses import ok

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.get("/")
@login_required
def list_page():
    notifications = NotificationService.list_for(current_user)
    NotificationService.mark_all_read(current_user)
    return render_template("notifications.html", notifications=notifications)


@notifications_bp.get("/api")
@login_required
def list_json():
    items = NotificationService.list_for(current_user)
    return ok([n.to_dict() for n in items])


@notifications_bp.get("/count")
@login_required
def count():
    return ok({"unread": NotificationService.unread_count(current_user)})


@notifications_bp.post("/read")
@login_required
def mark_read():
    NotificationService.mark_all_read(current_user)
    return ok(message="Marked read")