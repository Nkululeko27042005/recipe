from functools import wraps
from flask import current_app, abort
from flask_login import current_user
from .responses import error


def login_required_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return error("Authentication required", 401)
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        admins = current_app.config.get("ADMIN_USERNAMES", set())
        if current_user.username not in admins:
            abort(403)
        return f(*args, **kwargs)
    return wrapper