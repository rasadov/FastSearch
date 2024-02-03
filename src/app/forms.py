from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import Length, DataRequired, EqualTo, Email
import email_validator
from flask_login import current_user

class LoginForm(FlaskForm):
    email_address = EmailField(label='Email Adress', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[Length(6), DataRequired()])
    submit = SubmitField(label='Submit')

class RegisterForm(FlaskForm):
    email_address = EmailField(label='Email Adress', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[Length(8), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Submit')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label='Old Password', validators=[Length(8), DataRequired()])
    password = PasswordField(label='New Password', validators=[Length(8), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Submit')

class SetPasswordForm(FlaskForm):
    password = PasswordField(label='New Password', validators=[Length(8), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Submit')

class ChangeUsernameForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(3)])
    name = StringField(label='Name', validators=[Length(3)])
    submit = SubmitField(label='Submit')

# class ChangeEmailForm(FlaskForm):
#     email_address = EmailField(label='Email Adress', validators=[DataRequired(), Email()])
#     submit = SubmitField(label='Submit')

class DeleteAccountForm(FlaskForm):
    password = PasswordField(label='Password', validators=[Length(8), DataRequired()])
    submit = SubmitField(label='Submit')