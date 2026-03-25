from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import Email, EqualTo, InputRequired, Length


class RegistrationForm(FlaskForm):
    name = StringField("Full Name", validators=[InputRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=64)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    role = SelectField(
        "Role",
        choices=[("Student", "Student"), ("Teacher", "Teacher")],
        validators=[InputRequired()],
    )
    class_name = StringField("Class Name (Student)")
    subject = StringField("Subject (Teacher)")
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=64)])
    submit = SubmitField("Login")
