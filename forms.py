from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Optional

class RegisterForm(FlaskForm):
    """Form for registering a user."""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(),Email()])
    first_name = StringField("First name", validators=[InputRequired()])
    last_name = StringField("Last name", validators=[InputRequired()])

class LoginForm(FlaskForm):
    """form for logging in"""
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class NotesForm(FlaskForm):
    """form for users notes"""
    title = StringField("Title", validators=[InputRequired()])
    content = StringField("content", validators=[InputRequired()])

class UpdateNotesForm(FlaskForm):
    """form for users notes"""
    title = StringField("Title", validators=[Optional()])
    content = StringField("content", validators=[Optional()])

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""
