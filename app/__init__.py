import os
import click
from flask import Flask, render_template
from config import Config
from .extensions import db, migrate, login_manager, bcrypt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.recipes import recipes_bp
    from .routes.comments import comments_bp
    from .routes.reactions import reactions_bp
    from .routes.follows import follows_bp
    from .routes.feed import feed_bp
    from .routes.notifications import notifications_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")
    app.register_blueprint(comments_bp, url_prefix="/comments")
    app.register_blueprint(reactions_bp, url_prefix="/reactions")
    app.register_blueprint(follows_bp, url_prefix="/follows")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(feed_bp, url_prefix="/")

    # ---------- Error handlers ----------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/404.html"), 403

    # ---------- Template filters ----------
    @app.template_filter("timeago")
    def timeago(dt):
        from datetime import datetime
        if not dt:
            return ""
        delta = datetime.utcnow() - dt
        s = int(delta.total_seconds())
        if s < 60:      return f"{s}s ago"
        if s < 3600:    return f"{s // 60}m ago"
        if s < 86400:   return f"{s // 3600}h ago"
        if s < 2592000: return f"{s // 86400}d ago"
        return dt.strftime("%b %d, %Y")

    # ---------- CLI ----------
    @app.cli.command("seed")
    def seed_command():
        """Seed the database with sample data."""
        from .seed import seed
        seed()

    @app.cli.command("init-db")
    def init_db_command():
        """Create all tables (dev shortcut; prefer flask db upgrade)."""
        db.create_all()
        click.echo("✓ Tables created")

    return app