from collections import defaultdict
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from forms.student_forms import SubmissionForm
from models import Assignment, Attendance, Submission
from utils.analytics import student_analytics_data, student_dashboard_stats
from utils.decorators import role_required
from utils.extensions import db
from utils.file_utils import allowed_file, save_submission_file


student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required("Student")
def dashboard():
    stats = student_dashboard_stats(current_user.id)
    warning = "Attendance is below 75%! Please improve." if stats["attendance_percent"] < 75 else None
    return render_template("student/dashboard.html", stats=stats, warning=warning)


@student_bp.route("/attendance")
@login_required
@role_required("Student")
def attendance():
    records = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.date.desc()).all()

    subject_summary = defaultdict(lambda: {"present": 0, "total": 0})
    monthly_summary = defaultdict(lambda: {"present": 0, "total": 0})

    for record in records:
        subject_summary[record.subject]["total"] += 1
        monthly_key = record.date.strftime("%Y-%m")
        monthly_summary[monthly_key]["total"] += 1

        if record.status == "Present":
            subject_summary[record.subject]["present"] += 1
            monthly_summary[monthly_key]["present"] += 1

    subject_rows = []
    for subject, data in subject_summary.items():
        percent = round((data["present"] / data["total"]) * 100, 2) if data["total"] else 0
        subject_rows.append({"subject": subject, "present": data["present"], "total": data["total"], "percent": percent})

    monthly_rows = []
    for month, data in sorted(monthly_summary.items(), reverse=True):
        percent = round((data["present"] / data["total"]) * 100, 2) if data["total"] else 0
        monthly_rows.append({"month": month, "present": data["present"], "total": data["total"], "percent": percent})

    return render_template(
        "student/attendance.html",
        records=records,
        subject_rows=subject_rows,
        monthly_rows=monthly_rows,
    )


@student_bp.route("/assignments", methods=["GET"])
@login_required
@role_required("Student")
def assignments():
    all_assignments = Assignment.query.order_by(Assignment.deadline.asc()).all()
    now = datetime.utcnow()

    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    submission_map = {item.assignment_id: item for item in submissions}

    rows = []
    for assignment in all_assignments:
        submission = submission_map.get(assignment.id)
        status = "Not Submitted"
        if submission:
            status = submission.status
        elif assignment.deadline < now:
            status = "Not Submitted"

        rows.append({"assignment": assignment, "submission": submission, "status": status})

    return render_template("student/assignments.html", rows=rows)


@student_bp.route("/assignments/<int:assignment_id>/submit", methods=["GET", "POST"])
@login_required
@role_required("Student")
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    form = SubmissionForm()

    if form.validate_on_submit():
        file_obj = form.file.data
        if not allowed_file(file_obj.filename):
            flash("Invalid file format. Upload PDF or DOC/DOCX only.", "danger")
            return redirect(url_for("student.submit_assignment", assignment_id=assignment.id))

        file_name = save_submission_file(file_obj)
        existing = Submission.query.filter_by(assignment_id=assignment.id, student_id=current_user.id).first()

        if existing:
            existing.file_path = file_name
            existing.submitted_at = datetime.utcnow()
        else:
            db.session.add(
                Submission(
                    assignment_id=assignment.id,
                    student_id=current_user.id,
                    file_path=file_name,
                    submitted_at=datetime.utcnow(),
                )
            )

        db.session.commit()
        flash("Assignment submitted successfully.", "success")
        return redirect(url_for("student.assignments"))

    return render_template("student/submit_assignment.html", form=form, assignment=assignment)


@student_bp.route("/grades")
@login_required
@role_required("Student")
def grades():
    submissions = (
        Submission.query.filter_by(student_id=current_user.id)
        .filter(Submission.marks.isnot(None))
        .order_by(Submission.submitted_at.desc())
        .all()
    )
    return render_template("student/grades.html", submissions=submissions)


@student_bp.route("/analytics")
@login_required
@role_required("Student")
def analytics():
    data = student_analytics_data(current_user.id)
    return render_template("student/analytics.html", data=data)
