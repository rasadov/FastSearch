"""
This file contains all the routes related to the user's authentication.
~~~~~~~~~~~~~~~~~~~~~

Profile pages:
- `/register`: Renders the registration page and handles the registration form submission.
- `/login`: Renders the login page and handles the login functionality.
- `/login/google`: Handles the login with Google functionality.
- `/authorize/google`: Handles the authorization process for the user using Google OAuth.
- `/login/microsoft`: Handles the login with Microsoft functionality.
- `/authorize/microsoft`: Handles the authorization process for the user using Microsoft OAuth.
- `/logout`: Handles the logout functionality.

"""

from datetime import datetime

from flask import session, render_template, redirect, flash
from flask_login import login_user, logout_user


from app import app, db, oauth, login_required, logout_required, CURRENT_DOMAIN
from app.models import User
from app.utils.forms import RegisterForm, LoginForm

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

    Validates the registration form data. 
    If the form is valid and the email address is not already registered,
    a new user is created and added to the database.
    The user is then logged in and redirected to the verification page.
    If the email address is already registered, an error message is flashed.
    If there are any form validation errors, the error messages are flashed.

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
        flash("This Email is already used", category="danger")

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg[0], category="danger")
    return redirect("/register")


@app.get("/login")
@logout_required
def login_get():
    """
    Renders the login page.

    This function is responsible for rendering the login page.
    It creates an instance of the `LoginForm` class,
    and then passes it to the `render_template` function along with
    the template name "Account/login.html".
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

    Validates the login form data. If the form is valid and the user exists
    with the provided email address,
    and the password is correct, the user is logged in and redirected to the home page.
    If the user does not exist
    or the password is incorrect, an error message is flashed.

    Returns:
        If the form is submitted successfully, redirects to the home page.
        If there are form validation errors, renders the login page with the error messages.

    """
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user: User = User.query.filter_by(
            email_address=form.email_address.data
        ).first()
        if not attempted_user or not attempted_user.password_hash:
            flash("Email is not registered", category="danger")
            return redirect("/login")
        if attempted_user.chech_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user, remember=form.remember.data)
            return redirect("/")
        flash("Username or password is not correct", category="danger")
    return redirect("/login")


# OAuth2.0 with Google


@app.route("/login/google", methods=["GET", "POST"])
@logout_required
def login_with_google():
    """
    Redirects the user to the Google login page for authentication.

    Returns:
        The redirect response to the Google login page.
    """
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = CURRENT_DOMAIN + '/authorize/google'
    return google.authorize_redirect(redirect_uri)


@app.route("/authorize/google", methods=["GET", "POST"])
@logout_required
def authorize_google():
    """
    This route handles the authorization process for the user.
    It uses Google OAuth to authenticate the user and retrieve their information.

    Returns:
        redirects to the '/search' page.
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
    if not User.email_registered(user_to_add.email_address):
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

    # make the session permanent, so it keeps existing after browser gets closed
    session.permanent = True

    return redirect("/search")


# OAuth2.0 with Microsoft


@app.route("/login/microsoft", methods=["GET", "POST"])
@logout_required
def login_with_microsoft():
    """
    Redirects the user to the Microsoft login page for authentication.

    Returns:
        The redirect response to the Microsoft login page.
    """
    microsoft = oauth.create_client("microsoft")
    redirect_uri = CURRENT_DOMAIN + '/authorize/microsoft'
    return microsoft.authorize_redirect(redirect_uri)


@app.route("/authorize/microsoft", methods=["GET", "POST"])
@logout_required
def authorize_microsoft():
    """
    Authorizes the user using Microsoft OAuth and
    performs necessary actions based on the user's information.

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
    if not User.email_registered(user_to_add.email_address):
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

    # make the session permanent, so it keeps existing after browser gets closed
    session.permanent = True

    return redirect("/search")

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
