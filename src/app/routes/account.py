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

from models import *
from web import *

######## Profile pages ########


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
            login_user(user)
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
            login_user(attempted_user)
            return redirect("/")
        else:
            flash("Username or password is not correct", category="danger")


######## OAuth2.0 with Google ########


@app.get("/login/google")
@logout_required
def login_with_google():
    google = oauth.create_client("google")  # create the google oauth client
    redirect_uri = url_for("authorize_google", _external=True)
    return google.authorize_redirect(redirect_uri)


@app.post("/authorize/google")
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


######## OAuth2.0 with Microsoft ########


@app.get("/login/microsoft")
@logout_required
def login_with_microsoft():
    microsoft = oauth.create_client("microsoft")
    redirect_uri = url_for("authorize_microsoft", _external=True)
    return microsoft.authorize_redirect(redirect_uri)


@app.post("/authorize/microsoft")
@logout_required
def authorize_microsoft():
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


@app.get("/password/reset/<token>")
def reset_password_get(token):
    """
    Renders the reset password page.
    """
    form = ResetPasswordForm()
    user = User.verify_reset_token(token)
    if not user:
        flash("Token is invalid or has expired", "warning")
        return redirect(url_for("forgot_password_get"))

    return render_template("form_base.html", form=form)


@app.post("/password/reset/<token>")
def reset_password_post(token):
    """
    Handles the reset password form submission.

    Validates the reset password form data.
    If the form is valid, the user's password is updated in the database and a success message is flashed.
    If there are form validation errors, the error messages are flashed.

    Returns:
        If the form is submitted successfully, redirects to the login page.
        If there are form validation errors, renders the reset password page with the error messages.
    """
    form = ResetPasswordForm()
    user = User.verify_reset_token(token)
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("login_get"))


@app.get("/verification")
@login_required
def ask_of_verification():
    """
    Renders the verification page.
    """
    return render_template("Account/verification.html")


@app.post("/verification")
@login_required
def send_verification_email():
    """
    Handle the ask-of-verification route.

    This route is used to ask for email verification. It renders a form for the user to enter their verification code.
    If the form is submitted and valid, it sends an email to the user's email address with a verification token.
    The user is then redirected to the verify_email route.

    Returns:
        If the form is submitted and valid, the user is redirected to the verify_email route.
        Otherwise, the ask-of-verification page is rendered with the verification form.

    """
    user = User.query.filter_by(email_address=current_user.email_address).first()
    token = user.get_verification_token()
    send_email(
        user.email_address,
        f'Verify your email http://localhost:5000{ url_for("verify_email_get", token=token) }',
        "Email Verification",
        "Verification Code",
    )
    flash("Check your email for the verification link", "info")
    return redirect(url_for("profile_page"))


@app.get("/email/verify/<token>")
def verify_email_get(token):
    return render_template("Account/verify_email.html", token=token)


@app.post("/email/verify/<token>")
def verify_email_post(token):
    """
    Verify the email address using the provided token.

    Parameters:
    - token (str): The token used for email verification.

    Returns:
    - redirect: If the email is successfully verified, redirects to the home page.
    - redirect: If the token is invalid or expired, redirects to the 'unconfirmed' page.

    Raises:
    - None

    """
    try:
        user = User.verify_verification_token(token)
        if not user:
            flash("The confirmation link is invalid or has expired.", "danger")
            return redirect(url_for("unconfirmed"))
        user.confirmed_on = datetime.now().date()
        db.session.commit()
        if not current_user.is_authenticated:
            login_user(user)
        flash("Thank you for confirming your email address!", "success")
        return redirect("/profile")
    except SignatureExpired:
        flash("The confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("profile_page"))


# Logout page


@app.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# Profile management page


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_page():
    return render_template("Account/profile.html")


@app.route("/profile/password/change", methods=["GET", "POST"])
@login_required
def change_password():
    """
    This route allows the user to change their password.

    If the user hasn't set a password yet, a flash message will be displayed
    indicating that the password cannot be changed. Otherwise, a form will be
    rendered for the user to enter their old password and new password.

    If the form is submitted via POST request, the user's old password will be
    checked for correctness. If it is correct, the new password will be updated
    in the database and a success flash message will be displayed. If the old
    password is incorrect, an error flash message will be displayed.

    Returns:
        If the user is not logged in, they will be redirected to the home page.
        If the user hasn't set a password yet, they will be redirected to the home page.
        If the form is submitted and the old password is correct, the user will be
        redirected to their profile page.
        Otherwise, the change password form will be rendered.
    """
    if current_user.password_hash == None:
        flash(
            "You can't change your password because you haven't set it yet",
            category="danger",
        )
        return redirect("/")
    form = ChangePasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if current_user.chech_password_correction(
                attempted_password=form.old_password.data
            ):
                if form.password.data == form.old_password.data:
                    flash(
                        "New password can't be the same as old password",
                        category="danger",
                    )
                    return redirect("/change-password")
                current_user.password = form.password.data
                db.session.commit()
                flash("Password changed successfully", category="success")
                return redirect("/profile")
            else:
                flash("Old password is not correct", category="danger")
    return render_template("form_base.html", form=form)


@app.route("/profile/password/set", methods=["GET", "POST"])
@login_required
def set_password():
    """
    Route for setting a new password for the user.

    If the current user already has a password set, they will be redirected to their profile page.
    Otherwise, a form is displayed for the user to enter their new password.

    If the form is submitted via POST request and the entered password is valid, the user's password is updated
    in the database and a success message is flashed. The user is then redirected to their profile page.

    If the form is submitted via POST request but the entered password is not valid, an error message is flashed.

    If the request method is GET, the form is rendered for the user to enter their new password.

    Returns:
        A rendered template for the password form.

    """
    if current_user.password_hash:
        flash("You already have set password", category="danger")
        return redirect("/profile")
    form = SetPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            current_user.password = form.password.data
            db.session.commit()
            flash("Password changed successfully", category="success")
            return redirect("/profile")
        else:
            flash("Old password is not correct", category="danger")
    return render_template("form_base.html", form=form)


@app.route("/profile/username/change", methods=["GET", "POST"])
@login_required
def change_username():
    """
    This route handles the functionality to change the username and name of the current user.

    Methods:
    - GET: Renders the form with the current user's username and name pre-filled.
    - POST: Updates the username and name of the current user in the database.

    Returns:
    - GET: Renders the 'form_base.html' template with the form object.
    - POST: Redirects the user to the '/profile' route after updating the username and name.

    """
    form = ChangeUsernameForm()

    if request.method == "POST":
        if not form.username.data:
            form.username.validators = []
        if not form.name.data:
            form.name.validators = []
        if form.validate_on_submit():
            if (
                User.username_exists(form.username.data)
                and form.username.data != current_user.username
            ):
                flash("This username is already taken", category="danger")
                return redirect("/change-username")
            if (
                form.username.data == current_user.username
                and form.name.data == current_user.name
            ):
                flash("You didn't change anything", category="danger")
                return redirect("/change-username")
            if (
                form.username.data != current_user.username
                and form.name.data != current_user.name
            ):
                flash("Username and name were changed successfully", category="success")
            else:
                if form.username.data != current_user.username:
                    flash("Username changed successfully", category="success")
                if form.name.data != current_user.name:
                    flash("Name changed successfully", category="success")
            current_user.username = form.username.data
            current_user.name = form.name.data
            db.session.commit()
            return redirect("/profile")

    if request.method == "GET":
        form.username.data = current_user.username
        form.name.data = current_user.name

    return render_template("form_base.html", form=form)


@app.route("/profile/delete", methods=["GET", "POST"])
@login_required
def delete_account():
    """
    This route handles the deletion of a user account.

    Methods:
    - GET: Renders the delete account form.
    - POST: Deletes the user account if the password is correct.

    Returns:
    - GET: Renders the delete account form.
    - POST: Redirects to the home page after successful deletion.

    """
    form = DeleteAccountForm()
    if request.method == "POST":
        if form.validate_on_submit():
            if current_user.check_password_correction(
                attempted_password=form.password.data
            ):
                db.session.delete(current_user)
                db.session.commit()
                flash("Account deleted successfully", category="success")
                return redirect("/")
            else:
                flash("Password is not correct", category="danger")
    h1 = "Are you sure you want to delete your account?"
    return render_template("form_base.html", form=form, h1=h1)
