"""
This module contains Flask forms for user authentication and account management.
~~~~~~~~~~~~~~~~~~~~~

The forms in this module are used for various purposes such as user login, registration,
password change, username change, account deletion, and verification code submission.

Classes:
- `LoginForm`: Form for user login with email address and password fields.
- `RegisterForm`: Form for user registration with email address, password, and confirm password fields.
- `ChangePasswordForm`: Form for changing the user's password with old password, new password, and confirm password fields.
- `SetPasswordForm`: Form for setting a new password with password and confirm password fields.
- `ChangeUsernameForm`: Form for changing the user's username with username and name fields.
- `DeleteAccountForm`: Form for deleting the user's account with password field.
- `VerificationForm`: Form for submitting a verification code with a code field.
- `ForgotPasswordForm`: Form for submitting the user's email address to reset the password with email address field.
- `ResetPasswordForm`: Form for resetting the user's password with password and confirm password fields.
"""

from flask_wtf import FlaskForm
from wtforms import (EmailField, IntegerField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    """
    Form for user login.

    Fields:
    - email_address: EmailField for entering the user's email address.
    - password: PasswordField for entering the user's password.
    - submit: SubmitField for submitting the form.
    """

    email_address = EmailField(
        label="Email Address", validators=[DataRequired(), Email()]
    )
    password = PasswordField(label="Password", validators=[Length(6), DataRequired()])
    submit = SubmitField(label="Submit")


class RegisterForm(FlaskForm):
    """
    Form for user registration.

    Fields:
    - email_address: EmailField for entering the user's email address.
    - password: PasswordField for entering the user's password.
    - confirm_password: PasswordField for confirming the user's password.
    - submit: SubmitField for submitting the form.
    """

    email_address = EmailField(
        label="Email Address", validators=[DataRequired(), Email()]
    )
    password = PasswordField(label="Password", validators=[Length(8), DataRequired()])
    confirm_password = PasswordField(
        label="Confirm Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")


class ChangePasswordForm(FlaskForm):
    """
    Form for changing the user's password.

    Fields:
    - old_password: PasswordField for entering the user's old password.
    - password: PasswordField for entering the user's new password.
    - confirm_password: PasswordField for confirming the user's new password.
    - submit: SubmitField for submitting the form.
    """

    old_password = PasswordField(
        label="Old Password", validators=[Length(8), DataRequired()]
    )
    password = PasswordField(
        label="New Password", validators=[Length(8), DataRequired()]
    )
    confirm_password = PasswordField(
        label="Confirm Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")


class SetPasswordForm(FlaskForm):
    """
    Form for setting a new password.

    Fields:
    - password: PasswordField for entering the user's new password.
    - confirm_password: PasswordField for confirming the user's new password.
    - submit: SubmitField for submitting the form.
    """

    password = PasswordField(
        label="New Password", validators=[Length(8), DataRequired()]
    )
    confirm_password = PasswordField(
        label="Confirm Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")


class ChangeUsernameForm(FlaskForm):
    """
    Form for changing the user's username.

    Fields:
    - username: StringField for entering the user's new username.
    - name: StringField for entering the user's name.
    - submit: SubmitField for submitting the form.
    """

    username = StringField(
        label="Username",
        validators=[
            Length(3),
            Regexp(
                r"^[a-zA-Z0-9_]*$",
                message="Username must not contain special characters",
            ),
        ],
    )
    name = StringField(label="Name", validators=[Length(3)])
    submit = SubmitField(label="Submit")


class DeleteAccountForm(FlaskForm):
    """
    Form for deleting the user's account.

    Fields:
    - password: PasswordField for entering the user's password.
    - submit: SubmitField for submitting the form.
    """

    password = PasswordField(label="Password", validators=[Length(8), DataRequired()])
    submit = SubmitField(label="Submit")


class VerificationForm(FlaskForm):
    """
    Form for submitting a verification code.

    Fields:
    - code: IntegerField for entering the verification code.
    - submit: SubmitField for submitting the form.
    """

    code = IntegerField(label="Verification Code", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


class ForgotPasswordForm(FlaskForm):
    """
    Form for submitting the user's email address to reset the password.

    Fields:
    - email_address: EmailField for entering the user's email address.
    - submit: SubmitField for submitting the form.
    """

    email_address = EmailField(
        label="Email Address", validators=[DataRequired(), Email()]
    )
    submit = SubmitField(label="Submit")


class ResetPasswordForm(FlaskForm):
    """
    Form for resetting the user's password.

    Fields:
    - email_address: EmailField for entering the user's email address.
    - submit: SubmitField for submitting the form.
    """

    password = PasswordField(
        label="New Password", validators=[Length(8), DataRequired()]
    )
    confirm_password = PasswordField(
        label="Confirm Password", validators=[EqualTo("password"), DataRequired()]
    )
    submit = SubmitField(label="Submit")
