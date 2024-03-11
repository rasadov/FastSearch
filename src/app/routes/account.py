"""
This file contains all the routes related to the user's account management.
- The register page is defined here.
- The login page is defined here.
- The email verification page is defined here.
- The logout page is defined here.
- The profile management page is defined here.
"""

from web import *
from models import *

######## Profile pages ########

# Register and login page

@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register_page():
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
            print(f"There was an error: {err_msg[0]}")
    return render_template("Account/register.html", form=form)

@app.route('/login', methods=['GET','POST'])
@logout_required
def login_page():
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
    if current_user.is_confirmed():
        flash('Your email is already verified', category='info')
        return redirect('/profile')
    # form = SubmitForm()
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
    form = DeleteAccountForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.chech_password_correction(attempted_password=form.password.data):
                db.session.delete(current_user)
                db.session.commit()
                flash("Account deleted successfully", category='success')
                return redirect('/')
            else:
                flash("Password is not correct", category='danger')
    h1 = "Are you sure you want to delete your account?"
    return render_template('form_base.html', form=form, h1=h1)
