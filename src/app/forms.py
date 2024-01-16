from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import Length, DataRequired, EqualTo, Email
import email_validator

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(3, 25), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(6), DataRequired()])
    submit = SubmitField(label='Submit')

class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[Length(2), DataRequired()])
    username = StringField(label='Username', validators=[Length(2), DataRequired()])
    email_address = EmailField(label='Email Adress', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[Length(8), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Submit')