import os
import uuid

from flask import current_app

IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
DOC_EXT = IMAGE_EXT | {"pdf"}


def save_upload(file, subdir, allowed=IMAGE_EXT):
    """Save an uploaded file under static/uploads/<subdir>. Returns the static-relative path or None."""
    if not file or not file.filename or "." not in file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in allowed:
        return None
    name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.static_folder, "uploads", subdir)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, name))
    return f"uploads/{subdir}/{name}"
