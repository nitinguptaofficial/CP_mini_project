from flask_wtf import FlaskForm
from wtforms import DateField, DateTimeLocalField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, NumberRange


class AttendanceDateForm(FlaskForm):
    date = DateField("Attendance Date", validators=[InputRequired()])
    subject = StringField("Subject", validators=[InputRequired(), Length(min=2, max=100)])
    submit = SubmitField("Load Students")


class AssignmentForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(min=3, max=200)])
    description = TextAreaField("Description", validators=[InputRequired(), Length(min=5)])
    deadline = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M", validators=[InputRequired()])
    max_marks = IntegerField("Max Marks", validators=[InputRequired(), NumberRange(min=1, max=1000)])
    submit = SubmitField("Save Assignment")


class GradeForm(FlaskForm):
    marks = IntegerField("Marks", validators=[InputRequired(), NumberRange(min=0, max=1000)])
    feedback = TextAreaField("Feedback", validators=[Length(max=1000)])
    submit = SubmitField("Save Grade")
