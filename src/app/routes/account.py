"""
This file contains all the routes related to the user's account management.

Profile pages:
- `/register`: Renders the registration page and handles the registration form submission.
- `/login`: Renders the login page and handles the login functionality.
- `/login-with-google`: Handles the login with Google functionality.
- `/authorize`: Handles the authorization process for the user using Google OAuth.
- `/ask-of-verification`: Renders the ask for verification page and handles the verification form submission.
- `/verify-email`: Handles the verification of the user's email address.
- `/logout`: Handles the logout functionality.
- `/profile`: Renders the profile management page.
- `/change-password`: Allows the user to change their password.
- `/set-password`: Allows the user to set a new password.
- `/change-username`: Handles the functionality to change the username and name of the current user.
- `/delete-account`: Handles the deletion of a user account.

"""

from web import *
from models import *

######## Profile pages ########

@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register_page():
    """
    Renders the registration page and handles the registration form submission.

    GET: Renders the registration page with an empty registration form.
    POST: Validates the registration form data. If the form is valid and the email address is not already registered,
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
            user = User(password=form.password.data, email_address=form.email_address.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/ask-of-verification')
        else:
            flash('This Email is already used', category='danger')
    
    if form.errors != {}: 
        for err_msg in form.errors.values():
            flash(err_msg[0], category='danger')
    return render_template("Account/register.html", form=form)

@app.route('/login', methods=['GET','POST'])
@logout_required
def login_page():
    """
    Renders the login page and handles the login functionality.

    If the request method is GET, it renders the login page template.
    If the request method is POST, it validates the login form data.
    If the form data is valid, it checks if the user exists and the password is correct.
    If the user exists and the password is correct, it logs in the user and redirects to the home page.
    If the user does not exist or the password is incorrect, it displays an error message.

    Returns:
        If the request method is GET, it returns the rendered login page template.
        If the request method is POST and the form data is valid, it redirects to the home page.
        If the request method is POST and the form data is invalid, it returns the rendered login page template.
    """
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.chech_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            return redirect('/')
        else:
            flash("Username or password is not correct", category='danger')

    return render_template("Account/login.html", form=form)

@app.route('/login-with-google',methods=['GET','POST'])
@logout_required
def login_with_google():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
@logout_required
def authorize():
    """
    This route handles the authorization process for the user. It uses Google OAuth to authenticate the user and retrieve their information.

    Returns:
        redirect: If the user is already subscribed, it redirects them to the '/search' page. Otherwise, it redirects them to the '/#subscription' page.
    """
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info

    user_to_add = User(email_address=user['email'], name=user['name'], confirmed_on=str(datetime.now())[:19])
    if not User.user_exists(user_to_add.email_address):
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
    else:
        user_to_login = User.query.filter_by(email_address=user_to_add.email_address).first()
        if not user_to_login.is_confirmed():
            user_to_login.confirmed_on = str(datetime.now())[:19]
            db.session.commit()
        login_user(user_to_login)    
    session['profile'] = user_info
    session.permanent = True  # make the session permanent, so it keeps existing after browser gets closed
    
    if current_user.is_subscribed():
        return redirect('/search')
    
    return redirect('/#subscription')

# Verify email page

@app.route('/ask-of-verification', methods=['GET','POST'])
@login_required
@unconfirmed_required
def ask_for_verification():
    """
    Route handler for asking the user to verify their email address.

    If the user is already confirmed, a flash message is displayed and they are redirected to their profile page.
    If the request method is POST, a verification code is generated, sent to the user's email address, and a flash message is displayed.
    The user is then redirected to the email verification page.
    If the request method is GET, the verification page is rendered.

    Returns:
        If the request method is POST, redirects to '/verify-email'.
        If the request method is GET, renders the 'Account/verification.html' template.
    """
    if current_user.is_confirmed():
        flash('Your email is already verified', category='info')
        return redirect('/profile')
    if request.method == 'POST':
        global verification_code
        verification_code = randint(100000, 999999)
        send_email(f'Your verification code is {verification_code}', current_user.email_address, 'Email verification', 'Verification code for abyssara')
        flash('Email verification email sent!', category='info')
        return redirect('/verify-email')

    return render_template('Account/verification.html')

@app.route('/verify-email', methods=['GET','POST'])
@login_required
@unconfirmed_required
def verify_email():
    """
    This route handles the verification of user's email address.
    
    When a user submits the verification code through a form, this route checks if the code is correct.
    If the code is correct, the user's email is marked as verified and the user is redirected to the profile page if they are subscribed,
    otherwise they are redirected to the subscription section of the page.
    If the code is incorrect, an error message is flashed and the user is redirected back to the verification page.
    
    Returns:
        If the verification code is correct and the user is subscribed, redirects to '/profile'.
        If the verification code is correct and the user is not subscribed, redirects to '/#subscription'.
        If the verification code is incorrect, renders the 'Account/verify_email.html' template with the verification form.
    """
    
    global verification_code

    form = VerificationForm()
    if request.method == 'POST':        
        # Verification code is correct
        if form.code.data == verification_code:
            current_user.confirmed_on = str(datetime.now())[:19]
            db.session.commit()
            flash('Email verified successfully', category='success')
            
            if current_user.is_subscribed():
                return redirect('/profile')
            
            return redirect('/#subscription')
        
        # Verification code is not correct
        flash('Invalid verification code', category='danger')
        return render_template('Account/verify_email.html', form=form)
    return render_template('Account/verify_email.html', form=form)

# Logout page

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

# Profile management page 

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile_page():
    return render_template('Account/profile.html')
    
@app.route('/change-password', methods=['GET','POST'])
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
        flash("You can't change your password because you haven't set it yet", category='danger')
        return redirect('/')
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.chech_password_correction(attempted_password=form.old_password.data):
                if form.password.data == form.old_password.data:
                    flash("New password can't be the same as old password", category='danger')
                    return redirect('/change-password')
                current_user.password = form.password.data
                db.session.commit()
                flash("Password changed successfully", category='success')
                return redirect('/profile')
            else:
                flash("Old password is not correct", category='danger')
    return render_template('form_base.html', form=form)

@app.route('/set-password', methods=['GET','POST'])
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
        flash("You already have set password", category='danger')
        return redirect('/profile')
    form = SetPasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            current_user.password = form.password.data
            db.session.commit()
            flash("Password changed successfully", category='success')
            return redirect('/profile')
        else:
            flash("Old password is not correct", category='danger')
    return render_template('form_base.html', form=form)

@app.route('/change-username', methods=['GET','POST'])
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
    
    if request.method == 'POST':
        if not form.username.data:
            form.username.validators = []
        if not form.name.data:
            form.name.validators = []
        if form.validate_on_submit():
            if User.username_exists(form.username.data) and form.username.data != current_user.username:
                flash("This username is already taken", category='danger')
                return redirect('/change-username')
            if form.username.data == current_user.username and form.name.data == current_user.name:
                flash("You didn't change anything", category='danger')
                return redirect('/change-username')
            if form.username.data != current_user.username and form.name.data != current_user.name:
                flash("Username and name were changed successfully", category='success')
            else:            
                if form.username.data != current_user.username:
                    flash("Username changed successfully", category='success')
                if form.name.data != current_user.name:
                    flash("Name changed successfully", category='success')
            current_user.username = form.username.data
            current_user.name = form.name.data
            db.session.commit()
            return redirect('/profile')
        
    if request.method == 'GET':
        form.username.data = current_user.username
        form.name.data = current_user.name

    return render_template('form_base.html', form=form)

@app.route('/delete-account', methods=['GET','POST'])
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
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.check_password_correction(attempted_password=form.password.data):
                db.session.delete(current_user)
                db.session.commit()
                flash("Account deleted successfully", category='success')
                return redirect('/')
            else:
                flash("Password is not correct", category='danger')
    h1 = "Are you sure you want to delete your account?"
    return render_template('form_base.html', form=form, h1=h1)
