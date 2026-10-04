from functools import wraps
from flask_login import current_user
from .responses import error


def login_required_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return error("Authentication required", 401)
        return f(*args, **kwargs)
    return wrapper