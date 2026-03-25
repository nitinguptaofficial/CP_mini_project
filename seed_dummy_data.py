from datetime import datetime, timedelta

from app import app
from models import Assignment, Attendance, StudentProfile, Submission, TeacherProfile, User
from utils.extensions import bcrypt, db


# Seed script for quick demo during viva.
def create_user(name, email, password, role, class_name=None, subject=None):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return existing

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, password=hashed, role=role)
    db.session.add(user)
    db.session.flush()

    if role == "Student":
        db.session.add(StudentProfile(user_id=user.id, class_name=class_name or "BCA-1"))
    else:
        db.session.add(TeacherProfile(user_id=user.id, subject=subject or "Computer Science"))

    return user


def seed():
    with app.app_context():
        db.create_all()

        teacher = create_user(
            name="Dr. Mehta",
            email="teacher1@college.com",
            password="password123",
            role="Teacher",
            subject="Data Structures",
        )

        student1 = create_user(
            name="Aman Sharma",
            email="student1@college.com",
            password="password123",
            role="Student",
            class_name="BCA-2",
        )

        student2 = create_user(
            name="Riya Verma",
            email="student2@college.com",
            password="password123",
            role="Student",
            class_name="BCA-2",
        )

        db.session.commit()

        assignment = Assignment.query.filter_by(title="Linked List Implementation").first()
        if not assignment:
            assignment = Assignment(
                teacher_id=teacher.id,
                title="Linked List Implementation",
                description="Implement Singly Linked List operations in Python.",
                deadline=datetime.utcnow() + timedelta(days=7),
                max_marks=100,
            )
            db.session.add(assignment)
            db.session.commit()

        # Attendance samples.
        for day_offset in range(5):
            date_obj = (datetime.utcnow() - timedelta(days=day_offset)).date()
            for stu in [student1, student2]:
                present = "Present" if (stu.id + day_offset) % 2 == 0 else "Absent"
                found = Attendance.query.filter_by(
                    student_id=stu.id,
                    date=date_obj,
                    subject="Data Structures",
                ).first()
                if not found:
                    db.session.add(
                        Attendance(
                            student_id=stu.id,
                            date=date_obj,
                            status=present,
                            subject="Data Structures",
                            marked_by=teacher.id,
                        )
                    )

        # Submission sample for student1.
        existing_submission = Submission.query.filter_by(
            assignment_id=assignment.id,
            student_id=student1.id,
        ).first()

        if not existing_submission:
            db.session.add(
                Submission(
                    assignment_id=assignment.id,
                    student_id=student1.id,
                    file_path="sample_demo.pdf",
                    submitted_at=datetime.utcnow() - timedelta(days=1),
                    marks=86,
                    feedback="Good work. Improve edge case handling.",
                )
            )

        db.session.commit()
        print("Dummy data seeded successfully.")


if __name__ == "__main__":
    seed()
