from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField


class SubmissionForm(FlaskForm):
    file = FileField(
        "Upload File",
        validators=[
            FileRequired(),
            FileAllowed(["pdf", "doc", "docx"], "Only PDF and Word files are allowed."),
        ],
    )
    submit = SubmitField("Submit Assignment")
