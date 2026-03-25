import os

from flask import Blueprint, abort, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required

from models import Submission


core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "Teacher":
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))
    return render_template("index.html")


@core_bp.route("/uploads/<path:filename>")
@login_required
def download_file(filename):
    # Only allow downloading existing uploaded files that are tracked in DB.
    submission = Submission.query.filter_by(file_path=filename).first_or_404()

    if current_user.role == "Student" and submission.student_id != current_user.id:
        abort(403)

    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    return send_from_directory(upload_dir, filename, as_attachment=True)
