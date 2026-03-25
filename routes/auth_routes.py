from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user

from forms.auth_forms import LoginForm, RegistrationForm
from models import StudentProfile, TeacherProfile, User
from utils.extensions import bcrypt, db


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("Email already exists. Please login.", "danger")
            return redirect(url_for("auth.login"))

        # Hash password before storing to keep credentials secure.
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        role = form.role.data

        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            password=hashed_password,
            role=role,
        )
        db.session.add(user)
        db.session.flush()

        if role == "Student":
            profile = StudentProfile(user_id=user.id, class_name=(form.class_name.data or "BCA-1").strip())
        else:
            profile = TeacherProfile(user_id=user.id, subject=(form.subject.data or "General").strip())

        db.session.add(profile)
        db.session.commit()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("core.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful.", "success")
            if user.role == "Teacher":
                return redirect(url_for("teacher.dashboard"))
            return redirect(url_for("student.dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
