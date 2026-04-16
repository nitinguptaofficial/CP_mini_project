import os
from datetime import datetime, timedelta

from app import app
from models import Assignment, Attendance, StudentProfile, Submission, TeacherProfile, User
from utils.extensions import bcrypt, db


SEED_PASSWORD = os.environ.get("SEED_PASSWORD")


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
        if not SEED_PASSWORD:
            raise RuntimeError("Set SEED_PASSWORD before running the seed script.")

        db.create_all()

        teacher1 = create_user(
            name="Dr. Mehta",
            email="teacher1@college.com",
            password=SEED_PASSWORD,
            role="Teacher",
            subject="Data Structures",
        )

        teacher2 = create_user(
            name="Prof. Gupta",
            email="teacher2@college.com",
            password=SEED_PASSWORD,
            role="Teacher",
            subject="Database Systems",
        )

        student1 = create_user(
            name="Aman Sharma",
            email="student1@college.com",
            password=SEED_PASSWORD,
            role="Student",
            class_name="BCA-2",
        )

        student2 = create_user(
            name="Riya Verma",
            email="student2@college.com",
            password=SEED_PASSWORD,
            role="Student",
            class_name="BCA-2",
        )

        student3 = create_user(
            name="Karan Singh",
            email="student3@college.com",
            password=SEED_PASSWORD,
            role="Student",
            class_name="BCA-2",
        )

        student4 = create_user(
            name="Neha Gupta",
            email="student4@college.com",
            password=SEED_PASSWORD,
            role="Student",
            class_name="BCA-3",
        )

        db.session.commit()

        assignment1 = Assignment.query.filter_by(title="Linked List Implementation").first()
        if not assignment1:
            assignment1 = Assignment(
                teacher_id=teacher1.id,
                title="Linked List Implementation",
                description="Implement Singly Linked List operations in Python.",
                deadline=datetime.utcnow() + timedelta(days=7),
                max_marks=100,
            )
            db.session.add(assignment1)
            
        assignment2 = Assignment.query.filter_by(title="SQL Queries Assignment").first()
        if not assignment2:
            assignment2 = Assignment(
                teacher_id=teacher2.id,
                title="SQL Queries Assignment",
                description="Write complex SQL JOIN queries for the provided schema.",
                deadline=datetime.utcnow() + timedelta(days=5),
                max_marks=50,
            )
            db.session.add(assignment2)

        assignment3 = Assignment.query.filter_by(title="Binary Trees").first()
        if not assignment3:
            assignment3 = Assignment(
                teacher_id=teacher1.id,
                title="Binary Trees",
                description="Implement BST traversal techniques.",
                deadline=datetime.utcnow() + timedelta(days=10),
                max_marks=100,
            )
            db.session.add(assignment3)

        assignment4 = Assignment.query.filter_by(title="Normalization").first()
        if not assignment4:
            assignment4 = Assignment(
                teacher_id=teacher2.id,
                title="Normalization",
                description="Normalize the given schema to 3NF.",
                deadline=datetime.utcnow() + timedelta(days=12),
                max_marks=100,
            )
            db.session.add(assignment4)

        assignment5 = Assignment.query.filter_by(title="Graphs").first()
        if not assignment5:
            assignment5 = Assignment(
                teacher_id=teacher1.id,
                title="Graphs",
                description="Implement BFS and DFS.",
                deadline=datetime.utcnow() + timedelta(days=14),
                max_marks=100,
            )
            db.session.add(assignment5)

        db.session.commit()

        # Attendance samples for Data Structures
        for day_offset in range(15):
            date_obj = (datetime.utcnow() - timedelta(days=day_offset)).date()
            for stu in [student1, student2, student3]:
                # More mixed attendance
                present = "Present" if (stu.id + day_offset) % 3 != 0 else "Absent"
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
                            marked_by=teacher1.id,
                        )
                    )

        # Attendance samples for Database Systems
        for day_offset in range(15):
            date_obj = (datetime.utcnow() - timedelta(days=day_offset)).date()
            for stu in [student1, student2, student3, student4]:
                present = "Present" if (stu.id + day_offset) % 4 != 0 else "Absent"
                found = Attendance.query.filter_by(
                    student_id=stu.id,
                    date=date_obj,
                    subject="Database Systems",
                ).first()
                if not found:
                    db.session.add(
                        Attendance(
                            student_id=stu.id,
                            date=date_obj,
                            status=present,
                            subject="Database Systems",
                            marked_by=teacher2.id,
                        )
                    )

        # Submission sample for student1 on Assignment 1
        existing_sub1 = Submission.query.filter_by(
            assignment_id=assignment1.id,
            student_id=student1.id,
        ).first()

        if not existing_sub1:
            db.session.add(
                Submission(
                    assignment_id=assignment1.id,
                    student_id=student1.id,
                    file_path="sample_demo.pdf",
                    submitted_at=datetime.utcnow() - timedelta(days=1),
                    marks=86,
                    feedback="Good work. Improve edge case handling.",
                )
            )

        # Submission sample for student2 on Assignment 1
        existing_sub2 = Submission.query.filter_by(
            assignment_id=assignment1.id,
            student_id=student2.id,
        ).first()

        if not existing_sub2:
            db.session.add(
                Submission(
                    assignment_id=assignment1.id,
                    student_id=student2.id,
                    file_path="riya_linkedlist.pdf",
                    submitted_at=datetime.utcnow() - timedelta(days=2),
                    marks=92,
                    feedback="Excellent logic and code formatting.",
                )
            )

        # Submission sample for student3 on Assignment 2
        existing_sub3 = Submission.query.filter_by(
            assignment_id=assignment2.id,
            student_id=student3.id,
        ).first()

        if not existing_sub3:
            db.session.add(
                Submission(
                    assignment_id=assignment2.id,
                    student_id=student3.id,
                    file_path="karan_sql.pdf",
                    submitted_at=datetime.utcnow() - timedelta(days=1),
                    marks=40,
                    feedback="Good job, but missed the LEFT JOIN in query 3.",
                )
            )

        db.session.commit()
        print("Dummy data seeded successfully.")


if __name__ == "__main__":
    seed()
