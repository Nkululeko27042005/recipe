import os
from flask import Flask
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

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")
    app.register_blueprint(comments_bp, url_prefix="/comments")
    app.register_blueprint(reactions_bp, url_prefix="/reactions")
    app.register_blueprint(follows_bp, url_prefix="/follows")
    app.register_blueprint(feed_bp, url_prefix="/")

    return app