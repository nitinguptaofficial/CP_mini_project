from datetime import datetime

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from forms.teacher_forms import AssignmentForm, AttendanceDateForm, GradeForm
from models import Assignment, Attendance, StudentProfile, Submission
from utils.analytics import teacher_analytics_data, teacher_dashboard_stats
from utils.csv_utils import attendance_to_csv
from utils.decorators import role_required
from utils.extensions import db


teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
@login_required
@role_required("Teacher")
def dashboard():
    stats = teacher_dashboard_stats(current_user.id)
    return render_template("teacher/dashboard.html", stats=stats)


@teacher_bp.route("/attendance", methods=["GET", "POST"])
@login_required
@role_required("Teacher")
def attendance():
    form = AttendanceDateForm()

    selected_date = datetime.utcnow().date()
    selected_subject = current_user.teacher_profile.subject if current_user.teacher_profile else "General"

    if form.validate_on_submit() and "load_attendance" in request.form:
        selected_date = form.date.data
        selected_subject = form.subject.data

    if request.method == "POST" and "save_attendance" in request.form:
        selected_date = datetime.strptime(request.form.get("selected_date"), "%Y-%m-%d").date()
        selected_subject = request.form.get("selected_subject", "General")
        students = StudentProfile.query.order_by(StudentProfile.user_id.asc()).all()

        for student in students:
            status = "Present" if request.form.get(f"student_{student.user_id}") == "on" else "Absent"
            existing = Attendance.query.filter_by(
                student_id=student.user_id,
                date=selected_date,
                subject=selected_subject,
            ).first()

            if existing:
                existing.status = status
                existing.marked_by = current_user.id
            else:
                db.session.add(
                    Attendance(
                        student_id=student.user_id,
                        date=selected_date,
                        status=status,
                        subject=selected_subject,
                        marked_by=current_user.id,
                    )
                )

        db.session.commit()
        flash("Attendance saved successfully.", "success")
        return redirect(
            url_for(
                "teacher.attendance",
                date=selected_date.isoformat(),
                subject=selected_subject,
            )
        )

    if request.args.get("date"):
        selected_date = datetime.strptime(request.args.get("date"), "%Y-%m-%d").date()
    if request.args.get("subject"):
        selected_subject = request.args.get("subject")

    students = StudentProfile.query.order_by(StudentProfile.user_id.asc()).all()
    attendance_map = {
        record.student_id: record.status
        for record in Attendance.query.filter_by(date=selected_date, subject=selected_subject).all()
    }

    total_records = Attendance.query.filter_by(subject=selected_subject).count()
    present_records = Attendance.query.filter_by(subject=selected_subject, status="Present").count()
    attendance_overview = round((present_records / total_records) * 100, 2) if total_records else 0

    return render_template(
        "teacher/attendance_manage.html",
        form=form,
        students=students,
        attendance_map=attendance_map,
        selected_date=selected_date,
        selected_subject=selected_subject,
        attendance_overview=attendance_overview,
    )


@teacher_bp.route("/attendance/export")
@login_required
@role_required("Teacher")
def export_attendance():
    subject = request.args.get("subject", current_user.teacher_profile.subject)
    records = (
        Attendance.query.filter_by(subject=subject)
        .order_by(Attendance.date.desc())
        .all()
    )

    csv_rows = []
    for row in records:
        csv_rows.append(
            {
                "student_name": row.student.user.name,
                "student_email": row.student.user.email,
                "subject": row.subject,
                "date": row.date.isoformat(),
                "status": row.status,
            }
        )

    content = attendance_to_csv(csv_rows)
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=attendance_{subject}.csv"},
    )


@teacher_bp.route("/assignments", methods=["GET", "POST"])
@login_required
@role_required("Teacher")
def assignments():
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            teacher_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
            max_marks=form.max_marks.data,
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully.", "success")
        return redirect(url_for("teacher.assignments"))

    all_assignments = Assignment.query.filter_by(teacher_id=current_user.id).order_by(Assignment.deadline.asc()).all()
    return render_template("teacher/assignments.html", form=form, assignments=all_assignments)


@teacher_bp.route("/assignments/<int:assignment_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Teacher")
def edit_assignment(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id, teacher_id=current_user.id).first_or_404()
    form = AssignmentForm(obj=assignment)

    if form.validate_on_submit():
        assignment.title = form.title.data
        assignment.description = form.description.data
        assignment.deadline = form.deadline.data
        assignment.max_marks = form.max_marks.data
        db.session.commit()
        flash("Assignment updated.", "success")
        return redirect(url_for("teacher.assignments"))

    return render_template("teacher/assignment_edit.html", form=form, assignment=assignment)


@teacher_bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
@role_required("Teacher")
def delete_assignment(assignment_id):
    assignment = Assignment.query.filter_by(id=assignment_id, teacher_id=current_user.id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "info")
    return redirect(url_for("teacher.assignments"))


@teacher_bp.route("/submissions")
@login_required
@role_required("Teacher")
def submissions():
    assignment_id = request.args.get("assignment_id", type=int)
    teacher_assignments = Assignment.query.filter_by(teacher_id=current_user.id).order_by(Assignment.deadline.desc()).all()

    selected_assignment = None
    if assignment_id:
        selected_assignment = Assignment.query.filter_by(id=assignment_id, teacher_id=current_user.id).first()
    elif teacher_assignments:
        selected_assignment = teacher_assignments[0]

    rows = []
    if selected_assignment:
        students = StudentProfile.query.all()
        for student in students:
            submission = Submission.query.filter_by(
                assignment_id=selected_assignment.id,
                student_id=student.user_id,
            ).first()

            status = "Not Submitted"
            if submission:
                status = submission.status
            rows.append({"student": student, "submission": submission, "status": status})

    return render_template(
        "teacher/submissions.html",
        assignments=teacher_assignments,
        selected_assignment=selected_assignment,
        rows=rows,
    )


@teacher_bp.route("/submissions/<int:submission_id>/grade", methods=["GET", "POST"])
@login_required
@role_required("Teacher")
def grade_submission(submission_id):
    submission = (
        Submission.query.join(Assignment)
        .filter(Submission.id == submission_id, Assignment.teacher_id == current_user.id)
        .first_or_404()
    )

    form = GradeForm()
    if form.validate_on_submit():
        if form.marks.data > submission.assignment.max_marks:
            flash(f"Marks cannot exceed max marks ({submission.assignment.max_marks}).", "danger")
            return redirect(url_for("teacher.grade_submission", submission_id=submission.id))

        submission.marks = form.marks.data
        submission.feedback = form.feedback.data
        db.session.commit()
        flash("Grade updated.", "success")
        return redirect(url_for("teacher.submissions", assignment_id=submission.assignment_id))

    if request.method == "GET":
        form.marks.data = submission.marks
        form.feedback.data = submission.feedback

    return render_template("teacher/grade_submission.html", form=form, submission=submission)


@teacher_bp.route("/analytics")
@login_required
@role_required("Teacher")
def analytics():
    data = teacher_analytics_data(current_user.id)
    return render_template("teacher/analytics.html", data=data)
