from datetime import datetime, timezone

from flask_login import UserMixin

from utils.extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)
    teacher_profile = db.relationship("TeacherProfile", backref="user", uselist=False)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class StudentProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)

    attendances = db.relationship("Attendance", backref="student", lazy=True, cascade="all, delete")
    submissions = db.relationship("Submission", backref="student_user", lazy=True, cascade="all, delete")


class TeacherProfile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    subject = db.Column(db.String(100), nullable=False)

    assignments = db.relationship("Assignment", backref="teacher", lazy=True, cascade="all, delete")


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.user_id"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False, default="General")
    marked_by = db.Column(db.Integer, db.ForeignKey("teacher_profile.user_id"), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("student_id", "date", "subject", name="unique_attendance_per_day"),
    )


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher_profile.user_id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    submissions = db.relationship("Submission", backref="assignment", lazy=True, cascade="all, delete")


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.user_id"), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    marks = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("assignment_id", "student_id", name="unique_submission_per_assignment"),
    )

    @property
    def status(self):
        if self.submitted_at and self.assignment and self.submitted_at > self.assignment.deadline:
            return "Late"
        return "Submitted"
