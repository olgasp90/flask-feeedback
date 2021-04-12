from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[
                           InputRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=50)])
    email = StringField('Email', validators=[
                        InputRequired(), Email(), Length(min=12, max=50)])
    first_name = StringField('First Name', validators=[
                             InputRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[
                            InputRequired(), Length(min=3, max=30)])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField('Feedback Title', validators=[InputRequired(), Length(min=1, max=100)])
    content = StringField('Feedback content', validators=[InputRequired()])

class DeleteForm(FlaskForm):
    """blank form"""
