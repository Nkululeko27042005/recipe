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
        allowed_str = ", ".join(sorted(allowed))
        raise ValueError(f"Invalid {kind} format (.{ext}). Allowed formats: {allowed_str}")

    # Enforce file size limitation per file
    max_bytes = (current_app.config.get("MAX_IMAGE_BYTES", 5 * 1024 * 1024)
                 if kind == "image" else current_app.config.get("MAX_VIDEO_BYTES", 100 * 1024 * 1024))
    
    # Check size by seeking to end
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset pointer back to beginning

    if size > max_bytes:
        max_mb = max_bytes // (1024 * 1024)
        actual_mb = round(size / (1024 * 1024), 2)
        raise ValueError(f"{kind.capitalize()} '{file.filename}' is {actual_mb} MB, which exceeds the {max_mb} MB limit.")

    name = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    file.save(path)
    return name


def delete_file(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        os.remove(path)