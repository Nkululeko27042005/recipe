import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    
    # Render and modern cloud hosts provide DATABASE_URL starting with postgres://
    # SQLAlchemy requires postgresql://
    _db_url = os.getenv("DATABASE_URL", "sqlite:///recipe.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(__file__), "app", "static", "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 100 * 1024 * 1024))  # 100 MB default

    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_VIDEO_EXT = {"mp4", "webm", "mov"}

    # Max size for a single image (used in file_handler, not enforced by Flask globally)
    MAX_IMAGE_BYTES = 5 * 1024 * 1024   # 5 MB
    MAX_VIDEO_BYTES = 100 * 1024 * 1024 # 100 MB

    # Comma-separated usernames given admin rights, or empty for none
    ADMIN_USERNAMES = set(
        u.strip() for u in os.getenv("ADMIN_USERNAMES", "").split(",") if u.strip()
    )

    # Pagination
    RECIPES_PER_PAGE = 12
    FEED_LIMIT = 30