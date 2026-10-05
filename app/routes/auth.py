from flask import Blueprint, request, jsonify
from flask import flash, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from app.services.user_service import UserService
from app.models import User
from app.utils.responses import ok, created, error

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not username or not email or not password:
        return error("username, email and password are required", 422)

    preferences = data.get("preferences") or {
        "categories": [c.strip() for c in (data.get("categories") or "").split(",") if c.strip()],
        "dietary":    [d.strip() for d in (data.get("dietary") or "").split(",") if d.strip()],
    }

    try:
        user = UserService.create_user(username, email, password,
                                       bio=data.get("bio", ""),
                                       preferences=preferences)
    except ValueError as e:
        if request.is_json:
            return error(str(e), 409)
        flash(str(e), "danger")
        return redirect(url_for("auth.register_page"))

    login_user(user)

    if request.is_json:
        return created(user.to_dict(include_stats=True), "Registered successfully")
    flash("Welcome to RecipE!", "success")
    return redirect(url_for("feed.dashboard"))


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    identifier = (data.get("identifier") or data.get("email") or "").strip()
    password   = data.get("password") or ""
    user = User.query.filter(
        (User.email == identifier.lower()) | (User.username == identifier)
    ).first()

    if not user or not user.check_password(password):
        if request.is_json:
            return error("Invalid credentials", 401)
        flash("Invalid credentials", "danger")
        return redirect(url_for("auth.login_page"))

    login_user(user)

    if request.is_json:
        return ok(user.to_dict(include_stats=True), "Logged in")
    return redirect(url_for("feed.dashboard"))


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    if request.is_json or request.accept_mimetypes.best == "application/json":
        return ok(message="Logged out")
    flash("Logged out", "success")
    return redirect(url_for("auth.login_page"))


@auth_bp.get("/me")
def me():
    if not current_user.is_authenticated:
        return error("Not authenticated", 401)
    return ok(current_user.to_dict(include_stats=True))

from flask import render_template, redirect, url_for
from flask_login import current_user


@auth_bp.get("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("feed.dashboard"))
    return render_template("login.html")


@auth_bp.get("/register")
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("feed.dashboard"))
    return render_template("register.html")