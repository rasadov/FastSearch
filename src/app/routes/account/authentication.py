"""
This file contains all the routes related to the user's account management.
~~~~~~~~~~~~~~~~~~~~~

Profile pages:
- `/register`: Renders the registration page and handles the registration form submission.
- `/login`: Renders the login page and handles the login functionality.
- `/login/google`: Handles the login with Google functionality.
- `/authorize/google`: Handles the authorization process for the user using Google OAuth.
- `/login/microsoft`: Handles the login with Microsoft functionality.
- `/authorize/microsoft`: Handles the authorization process for the user using Microsoft OAuth.
- `/password/forgot`: Handles the forgot password functionality.
- `/password/reset/<token>`: Handles the reset password functionality using a reset token.
- `/verification`: Handles the ask-of-verification route.
- `/email/verify/<token>`: Handles the email verification functionality using the provided token.
- `/logout`: Handles the logout functionality.
- `/profile`: Renders the profile management page.
- `/profile/password/change`: Allows the user to change their password.
- `/profile/password/set`: Allows the user to set a new password.
- `/profile/username/change`: Handles the functionality to change the username and name of the current user.
- `/profile/delete`: Handles the deletion of a user account.

"""

from models import User
from web import (app, db, session, oauth, render_template,
                url_for, redirect, flash, login_user,
                logout_user, login_required,
                logout_required, send_email, datetime)
from forms import RegisterForm, LoginForm, ForgotPasswordForm

# login and registration routes

@app.get("/register")
@logout_required
def register_get():
    """
    Renders the registration page.


    Returns:
        The rendered registration page template.
    """
    form = RegisterForm()
    return render_template("Account/register.html", form=form)


@app.post("/register")
def register_post():
    """
    Handles the registration form submission

    Validates the registration form data. If the form is valid and the email address is not already registered,
    a new user is created and added to the database. The user is then logged in and redirected to the verification page.
    If the email address is already registered, an error message is flashed. If there are any form validation errors,
    the error messages are flashed.

    Returns:
        If the form is submitted successfully, redirects to the verification page.
        If there are form validation errors, renders the registration page with the error messages.


    """
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email_address=form.email_address.data).count():
            user = User(
                password=form.password.data, email_address=form.email_address.data
            )
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=form.remember.data)
            return redirect("/verification")
        else:
            flash("This Email is already used", category="danger")

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg[0], category="danger")


@app.get("/login")
@logout_required
def login_get():
    """
    Renders the login page.

    This function is responsible for rendering the login page. It creates an instance of the `LoginForm` class,
    and then passes it to the `render_template` function along with the template name "Account/login.html".
    The rendered HTML page is returned as the response.

    Returns:
        str: The rendered HTML page of the login form.

    """
    form = LoginForm()
    return render_template("Account/login.html", form=form)


@app.post("/login")
@logout_required
def login_post():
    """
    Handles the login form submission.

    Validates the login form data. If the form is valid and the user exists with the provided email address,
    and the password is correct, the user is logged in and redirected to the home page. If the user does not exist
    or the password is incorrect, an error message is flashed.

    Returns:
        If the form is submitted successfully, redirects to the home page.
        If there are form validation errors, renders the login page with the error messages.

    """
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(
            email_address=form.email_address.data
        ).first()
        if attempted_user and attempted_user.chech_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user, remember=form.remember.data)
            return redirect("/")
        else:
            flash("Username or password is not correct", category="danger")


# OAuth2.0 with Google 


@app.get("/login/google")
@logout_required
def login_with_google():
    """
    Redirects the user to the Google login page for authentication.

    Returns:
        The redirect response to the Google login page.
    """
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = url_for("authorize_google", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.get("/authorize/google")
@logout_required
def authorize_google():
    """
    This route handles the authorization process for the user. It uses Google OAuth to authenticate the user and retrieve their information.

    Returns:
        redirect: If the user is already subscribed, it redirects them to the '/search' page. Otherwise, it redirects them to the '/#subscription' page.
    """
    google = oauth.create_client("google")  # create the google oauth client
    token = (
        google.authorize_access_token()
    )  # Access token from google (needed to get user info)
    resp = google.get("userinfo")  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info

    user_to_add = User(
        email_address=user["email"],
        name=user["name"],
        confirmed_on=datetime.now().date(),
    )
    if not User.user_exists(user_to_add.email_address):
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
    else:
        user_to_login = User.query.filter_by(
            email_address=user_to_add.email_address
        ).first()
        if not user_to_login.is_confirmed():
            user_to_login.confirmed_on = datetime.now().date()
            db.session.commit()
        login_user(user_to_login)
    session["profile"] = user_info
    session.permanent = True  # make the session permanent, so it keeps existing after browser gets closed

    return redirect("/search")


# OAuth2.0 with Microsoft


@app.get("/login/microsoft")
@logout_required
def login_with_microsoft():
    """
    Redirects the user to the Microsoft login page for authentication.

    Returns:
        The redirect response to the Microsoft login page.
    """
    microsoft = oauth.create_client("microsoft")
    redirect_uri = url_for("authorize_microsoft", _external=True)
    return microsoft.authorize_redirect(redirect_uri)


@app.get("/authorize/microsoft")
@logout_required
def authorize_microsoft():
    """
    Authorizes the user using Microsoft OAuth and performs necessary actions based on the user's information.

    Returns:
        A redirect response to the "/search" page.
    """
    microsoft = oauth.create_client("microsoft")
    token = microsoft.authorize_access_token()
    resp = microsoft.get("userinfo")
    user_info = resp.json()
    user = oauth.microsoft.userinfo()
    user_to_add = User(
        email_address=user["mail"],
        name=user["givenName"],
        confirmed_on=datetime.now().date(),
    )
    if not User.user_exists(user_to_add.email_address):
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
    else:
        user_to_login = User.query.filter_by(
            email_address=user_to_add.email_address
        ).first()
        if not user_to_login.is_confirmed():
            user_to_login.confirmed_on = datetime.now().date()
            db.session.commit()
        login_user(user_to_login)
    session["profile"] = user_info
    session.permanent = True  # make the session permanent, so it keeps existing after browser gets closed
    return redirect("/search")


# Pages for email verification and password reset via email


@app.get("/password/forgot")
def forgot_password_get():
    """
    Handle the forgot password functionality.

    This function is responsible for handling the forgot password feature. It checks if the request method is POST and the form is valid. If the form is valid, it retrieves the user with the provided email address from the database. If the user exists, it generates a reset token, sends an email to the user with the reset password link, and displays a flash message to check the email for instructions. If the user does not exist, it displays a flash message indicating that the email was not found.

    Returns:
        A rendered template 'form_base.html' with the form object.

    """
    form = ForgotPasswordForm()
    return render_template("form_base.html", form=form)


@app.post("/password/forgot")
def forgot_password_post():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            token = user.get_reset_token()
            send_email(
                user.email_address,
                f'Link to reset the password 127.0.0.1:5000{ url_for("reset_password_get", token=token) }',
                "Reset Password",
                "Password Reset Request",
            )
            flash("Check your email for instructions to reset your password", "info")
        else:
            flash("Email not found", "warning")

# Logout page

@app.get("/logout")
@login_required
def logout():
    """
    Logs out the user and redirects to the home page.

    Returns:
        A redirect response to the home page.
    """
    logout_user()
    return redirect("/")


# Profile management page
