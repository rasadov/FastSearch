"""
This module defines the routes for the user profile and account management.

The following routes are defined:
- `/profile`: Renders the profile management page.
- `/profile/password/change`: Allows the user to change their password.
- `/profile/password/set`: Allows the user to set a new password.
- `/profile/username/change`: Handles the functionality to change the username
  and name of the current user.
- `/profile/delete`: Handles the deletion of a user account.
- `/password/forgot`: Handles the forgot password functionality.
- `/password/reset/<token>`: Handles the reset password functionality using a reset token.
- `/verification`: Handles the ask-of-verification route.
- `/email/verify/<token>`: Handles the email verification functionality using the provided token.
"""

from app import (app, login_required, render_template,
                flash, redirect, url_for, login_user,
                request, db, current_user,
                datetime, SignatureExpired)
from app.models import User, Cart
from app.__forms__ import (ChangePasswordForm, SetPasswordForm, ChangeUsernameForm,
                DeleteAccountForm, ResetPasswordForm, ForgotPasswordForm)
from app.__email__sender__ import send_email


@app.get("/profile")
@login_required
def profile_get():
    """
    Retrieve the user's profile and render the profile page.

    Returns:
        The rendered profile page with the user's cart items.
    """
    cart = Cart.items(current_user.id)
    return render_template("Account/profile.html", cart=cart)


@app.get("/profile/password/change")
@login_required
def change_password_get():
    """
    Renders the change password form for the user.

    If the user's password hash is None, redirects to the password set page.
    
    Returns:
        A rendered template of the change password form.
    """
    if not current_user.password_hash:
        return redirect("/profile/password/set")
    form = ChangePasswordForm()

    return render_template("form_base.html",h1="Change passwrod", form=form)

@app.post("/profile/password/change")
@login_required
def change_password_post():
    """
    Handles the POST request for changing the user's password.

    This function is triggered when the user submits the change password form.
    It validates the form data, checks if the old password is correct, and updates
    the user's password in the database if all conditions are met.

    Returns:
        A redirect response to the user's profile page if the password is changed
        successfully, or a redirect response to the change password page with an
        appropriate flash message if there are any errors.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.password.data == form.old_password.data:
            flash(
                "New password can't be the same as old password",
                category="danger",
            )
            return redirect("/profile/password/change")
        if current_user.check_password_correction(
            attempted_password=form.old_password.data
        ):
            current_user.password = form.password.data
            db.session.commit()
            flash("Password changed successfully", category="success")
            return redirect("/profile")
        flash("Old password is not correct", category="danger")
    return redirect("/profile/password/change")

@app.get("/profile/password/set")
@login_required
def set_password_get():
    """
    Renders the set password form for the user.

    If the user's password hash is not None, redirects to the change password page.

    Returns:
        A rendered template of the set password form.
    """
    if current_user.password_hash:
        return redirect("/profile/password/change")
    form = SetPasswordForm()

    return render_template("form_base.html", form=form)

@app.post("/profile/password/set")
def set_password_post():
    """
    Handles the POST request for setting a new password for the user.

    This function is triggered when the user submits the set password form.
    It validates the form data and updates the user's password in the database
    if all conditions are met.

    Returns:
        A redirect response to the user's profile page if the password is set
        successfully, or a redirect response to the set password page with an
        appropriate flash message if there are any errors.

    """
    form = SetPasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.commit()
        flash("Password changed successfully", category="success")
        return redirect("/profile")
    flash("Old password is not correct", category="danger")
    return redirect("/profile/password/set")

@app.get("/profile/username/change")
@login_required
def change_username_get():
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
    form.username.data = current_user.username
    form.name.data = current_user.name

    return render_template("form_base.html", h1="Change Username", form=form)

@app.post("/profile/username/change")
@login_required
def change_username_post():
    """
    Handles the POST request for changing the username and name of the user.

    This function is triggered when the user submits the change username form.
    It validates the form data and updates the user's username and name in the database
    if all conditions are met.

    Returns:
        A redirect response to the user's profile page if the username and name are changed
        successfully, or a redirect response to the change username page with an
        appropriate flash message if there are any errors.

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
                return redirect("/profile/username/change")
            if (
                form.username.data == current_user.username
                and form.name.data == current_user.name
            ):
                flash("You didn't change anything", category="danger")
                return redirect("/profile/username/change")
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
    return redirect("/profile/username/change")

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

    return render_template("form_base.html", h1='Reset Password' ,form=form)


@app.post("/password/reset/<token>")
def reset_password_post(token):
    """
    Handles the reset password form submission.

    Validates the reset password form data.
    If the form is valid, the user's password is updated in the database and
    a success message is flashed.
    If there are form validation errors, the error messages are flashed.

    Returns:
        If the form is submitted successfully, redirects to the login page.
        If there are form validation errors, renders the reset password page
        with the error messages.
    """
    form = ResetPasswordForm()
    user = User.verify_reset_token(token)
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("login_get"))
    return redirect(url_for("reset_password_get", token=token))


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

    This route is used to ask for email verification.
    It renders a form for the user to enter their verification code.
    If the form is submitted and valid,
    it sends an email to the user's email address with a verification token.
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
    return redirect(url_for("profile_get"))


@app.get("/email/verify/<token>")
def verify_email_get(token):
    """
    Renders the verify_email.html template with the provided token.

    Parameters:
    - token (str): The verification token.

    Returns:
    - The rendered template.
    """
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
        return redirect(url_for("profile_get"))

@app.get("/password/forgot")
def forgot_password_get():
    """
    Handle the forgot password functionality.

    This function is responsible for handling the forgot password feature.
    It checks if the request method is POST and the form is valid.
    If the form is valid, it retrieves the user with the provided email address from the database.
    If the user exists, it generates a reset token, sends an email to the user with the reset
    password link, and displays a flash message to check the email for instructions.
    If the user does not exist,
    it displays a flash message indicating that the email was not found.

    Returns:
        A rendered template 'form_base.html' with the form object.

    """
    form = ForgotPasswordForm()
    return render_template("form_base.html", form=form)


@app.post("/password/forgot")
def forgot_password_post():
    """
    Handle the POST request for the 'forgot password' functionality.

    This function validates the form data submitted by the user. If the form is valid,
    it retrieves the user with the provided email address from the database. If the user
    exists, a password reset token is generated and an email is sent to the user with a
    link to reset their password. If the user does not exist, a warning message is flashed.

    Returns:
        None
    """
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            token = user.get_reset_token()
            url = f"127.0.0.1:5000/password/reset/{token}"
            send_email(
                user.email_address,
                f"Link to reset the password: {url}",
                "Reset Password",
                "Password Reset Request",
            )
            flash("Check your email for instructions to reset your password", "info")
        else:
            flash("Email not found", "warning")


@app.get("/profile/delete")
@login_required
def delete_account_get():
    """
    This route handles the deletion of a user account.
    
    Methods:
        Renders the delete account form.

    Returns:
        - Renders the delete account form.
    """
    form = DeleteAccountForm()
    h1 = "Are you sure you want to delete your account?"
    return render_template("form_base.html", form=form, h1=h1)

@app.post("/profile/delete")
@login_required
def delete_account_post():
    """
    Handles the POST request for deleting the user's account.

    This function is triggered when the user submits the delete account form.
    It validates the form data and deletes the user's account from the database
    if all conditions are met.

    Returns:
        A redirect response to the home page if the account is deleted
        successfully, or a redirect response to the delete account page with an
        appropriate flash message if there are any errors.

    """
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if current_user.check_password_correction(
            attempted_password=form.password.data
        ):
            db.session.delete(current_user)
            db.session.commit()
            flash("Account deleted successfully", category="success")
            return redirect("/")
        flash("Password is not correct", category="danger")
    return redirect("/profile/delete")
