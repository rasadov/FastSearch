from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Length, DataRequired

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(3, 25), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(6), DataRequired()])
    submit = SubmitField(label='Submit')

class RegisterForm(FlaskForm):
    username = StringField(label='Username', validators=[Length(3, 30), DataRequired()])
    name = StringField(label='Username', validators=[Length(3, 30)])
    password = PasswordField(label='Password', validators=[Length(6), DataRequired()])
    confirm_password = PasswordField(label='Password', validators=[Length(6), DataRequired()])
    submit = SubmitField(label='Submit')