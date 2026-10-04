import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def _ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def save_file(file, kind="image"):
    if not file or file.filename == "":
        return None
    ext = _ext(file.filename)
    allowed = (current_app.config["ALLOWED_IMAGE_EXT"]
               if kind == "image" else current_app.config["ALLOWED_VIDEO_EXT"])
    if ext not in allowed:
        raise ValueError(f"Invalid {kind} extension: {ext}")
    name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    file.save(path)
    return name


def delete_file(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)