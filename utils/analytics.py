from collections import defaultdict
from datetime import datetime

from models import Assignment, Attendance, StudentProfile, Submission, User
from utils.chart_utils import bar_chart, line_chart


def attendance_percentage_for_student(student_id):
    total = Attendance.query.filter_by(student_id=student_id).count()
    if total == 0:
        return 0.0
    present = Attendance.query.filter_by(student_id=student_id, status="Present").count()
    return round((present / total) * 100, 2)


def teacher_dashboard_stats(teacher_id):
    total_students = StudentProfile.query.count()
    total_attendance = Attendance.query.count()
    present_attendance = Attendance.query.filter_by(status="Present").count()
    attendance_overview = round((present_attendance / total_attendance) * 100, 2) if total_attendance else 0

    now = datetime.utcnow()
    pending_assignments = Assignment.query.filter(
        Assignment.teacher_id == teacher_id, Assignment.deadline >= now
    ).count()

    recent_submissions = (
        Submission.query.join(Assignment)
        .filter(Assignment.teacher_id == teacher_id)
        .order_by(Submission.submitted_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_students": total_students,
        "attendance_overview": attendance_overview,
        "pending_assignments": pending_assignments,
        "recent_submissions": recent_submissions,
    }


def teacher_analytics_data(teacher_id):
    assignments = Assignment.query.filter_by(teacher_id=teacher_id).all()
    assignment_ids = [item.id for item in assignments]

    graded = Submission.query.filter(
        Submission.assignment_id.in_(assignment_ids), Submission.marks.isnot(None)
    ).all() if assignment_ids else []

    class_average = (
        round(sum(item.marks for item in graded) / len(graded), 2)
        if graded
        else 0
    )

    student_marks = defaultdict(list)
    for item in graded:
        student_marks[item.student_id].append(item.marks)

    top_performers = []
    for student_id, marks_list in student_marks.items():
        user = User.query.get(student_id)
        if user:
            top_performers.append(
                {
                    "name": user.name,
                    "avg": round(sum(marks_list) / len(marks_list), 2),
                }
            )
    top_performers = sorted(top_performers, key=lambda x: x["avg"], reverse=True)[:5]

    low_attendance = []
    for profile in StudentProfile.query.all():
        total = Attendance.query.filter_by(student_id=profile.user_id).count()
        if total == 0:
            continue
        present = Attendance.query.filter_by(student_id=profile.user_id, status="Present").count()
        percent = round((present / total) * 100, 2)
        if percent < 75:
            low_attendance.append(
                {
                    "name": profile.user.name,
                    "percent": percent,
                }
            )

    total_possible = len(assignments) * StudentProfile.query.count()
    total_submitted = Submission.query.filter(Submission.assignment_id.in_(assignment_ids)).count() if assignment_ids else 0
    submission_rate = round((total_submitted / total_possible) * 100, 2) if total_possible else 0

    # ── generate matplotlib charts ──
    top_chart = bar_chart(
        [p["name"] for p in top_performers],
        [p["avg"] for p in top_performers],
        title="Top Performing Students",
        ylabel="Average Marks",
        color="#4f46e5",
    )
    low_chart = bar_chart(
        [s["name"] for s in low_attendance],
        [s["percent"] for s in low_attendance],
        title="Low Attendance (%)",
        ylabel="Attendance %",
        color="#ef4444",
    )

    return {
        "class_average": class_average,
        "top_performers": top_performers,
        "low_attendance": low_attendance,
        "submission_rate": submission_rate,
        "top_chart": top_chart,
        "low_chart": low_chart,
    }


def student_dashboard_stats(student_id):
    attendance_percent = attendance_percentage_for_student(student_id)

    now = datetime.utcnow()
    upcoming_deadlines = Assignment.query.filter(Assignment.deadline >= now).order_by(Assignment.deadline.asc()).limit(5).all()

    recent_grades = (
        Submission.query.filter_by(student_id=student_id)
        .filter(Submission.marks.isnot(None))
        .order_by(Submission.submitted_at.desc())
        .limit(5)
        .all()
    )

    return {
        "attendance_percent": attendance_percent,
        "upcoming_deadlines": upcoming_deadlines,
        "recent_grades": recent_grades,
    }


def student_analytics_data(student_id):
    submissions = Submission.query.filter_by(student_id=student_id).all()

    performance_labels = [entry.assignment.title for entry in submissions if entry.marks is not None]
    performance_values = [float(entry.marks) for entry in submissions if entry.marks is not None]

    subject_map = defaultdict(list)
    for entry in submissions:
        if entry.marks is None:
            continue
        subject = entry.assignment.teacher.subject
        subject_map[subject].append(float(entry.marks))

    subject_labels = list(subject_map.keys())
    subject_values = [round(sum(values) / len(values), 2) for values in subject_map.values()]

    suggestions = []
    attendance = attendance_percentage_for_student(student_id)
    if attendance < 75:
        suggestions.append("Your attendance is below 75%. Attend classes regularly.")

    if performance_values:
        avg_marks = sum(performance_values) / len(performance_values)
        if avg_marks < 50:
            suggestions.append("Average marks are below 50. Revise fundamentals and practice weekly.")
        elif avg_marks < 70:
            suggestions.append("You are improving. Focus on weak topics and past assignments.")
        else:
            suggestions.append("Great performance. Maintain consistency and attempt advanced problems.")
    else:
        suggestions.append("No graded submissions yet. Submit assignments before deadline.")

    # ── generate matplotlib charts ──
    perf_chart = line_chart(
        performance_labels,
        performance_values,
        title="Performance Trend",
        ylabel="Marks",
        color="#4f46e5",
    )
    subj_chart = bar_chart(
        subject_labels,
        subject_values,
        title="Subject-wise Comparison",
        ylabel="Average Marks",
        color="#8b5cf6",
    )

    return {
        "performance_labels": performance_labels,
        "performance_values": performance_values,
        "subject_labels": subject_labels,
        "subject_values": subject_values,
        "suggestions": suggestions,
        "perf_chart": perf_chart,
        "subj_chart": subj_chart,
    }
