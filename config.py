import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///recipe.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB (for videos)
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_VIDEO_EXT = {"mp4", "webm", "mov"}