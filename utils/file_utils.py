import os
import uuid
from pathlib import Path

from flask import current_app
from werkzeug.utils import secure_filename


# Validate extension by reading app config.
def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


# Save upload with unique secure filename.
def save_submission_file(storage_file):
    original_name = secure_filename(storage_file.filename)
    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    final_path = upload_dir / unique_name
    storage_file.save(final_path)
    return unique_name


def absolute_upload_path(file_name):
    return os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
