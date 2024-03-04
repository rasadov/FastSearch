import random
from flask import redirect, render_template, request, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, current_user
from web import *
from models import *
from forms import *
from email_sender import send_email

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User,int(user_id))
    except (ValueError, TypeError):
        return None 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')

# Home page

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        print(current_user.is_admin())
    return render_template("Main/index.html")

# Product search page

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = Product.query.filter(Product.title.ilike(f'%{search_query}%')).all()
        return render_template('Main/search_results.html', results=results, query=search_query)
    if request.method == 'GET':
        return render_template('Main/search.html')


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

    user_to_add = User(email_address=user['email'], name=user['name'], is_confirmed=True, confirmed_on=datetime.now())
    if not User.user_exists(user_to_add.email_address):
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
    else:
        user_to_login = User.query.filter_by(email_address=user_to_add.email_address).first()
        if not user_to_login.is_confirmed:
            user_to_login.is_confirmed = True
            user_to_login.confirmed_on = datetime.now()
            db.session.commit()
        login_user(user_to_login)    
    session['profile'] = user_info
    session.permanent = True  # make the session permanent, so it keeps existing after browser gets closed
    return redirect('/')

# Verify email page

@app.route('/ask-of-verification', methods=['GET','POST'])
@login_required
@unconfirmed_required
def ask_for_verification():
    if current_user.is_confirmed:
        flash('Your email is already verified', category='info')
        return redirect('/profile')
    # form = SubmitForm()
    if request.method == 'POST':
            global verification_code
            verification_code = random.randint(100000, 999999)
            send_email(f'Your verification code is {verification_code}', current_user.email_address)
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
            current_user.is_confirmed = True
            current_user.confirmed_on = datetime.now()
            db.session.commit()
            flash('Email verified successfully', category='success')
            return redirect('/profile')
        
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
            if User.check_username(form.username.data) and form.username.data != current_user.username:
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

# Admin page

@app.route('/admin', methods=['GET','POST'])
@admin_required
def admin_page():
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template('Admin/admin.html', count_of_products=count_of_products, count_of_users=count_of_users)


@app.route('/admin/users', methods=['GET','POST'])
@admin_required
def admin_users_page(page=1):
    form = SearchForm()
    total_pages = User.query.count() // 10

    search_query = ''           

    if request.method == 'POST':
        if form.validate_on_submit():
            search_query = form.search.data
    try:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        )
        amount_of_users = users.count()
    except IndexError:
        users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        )
        amount_of_users = users.count()
    return render_template('Admin/users.html', users=users, page=page, total_pages=total_pages, search_query=search_query, amount_of_users=amount_of_users, form=form)
    
@app.route('/admin/user/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_edit_page(id):
    user = User.query.get(id)
    if request.method == 'POST':

        # Username, name, email
        username = request.form.get('username')
        name = request.form.get('name')
        email_address = request.form.get('email')

        if username != user.username:
            if User.check_username(username):
                flash("This username is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.username = username
        if name != user.name:
            user.name = name
        if email_address != user.email_address:
            if User.query.filter_by(email_address=email_address).count():
                flash("This email is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.email_address = email_address
            
        # Confimation
        confirmation = request.form.get('confirmed')
        if confirmation == 'True':
            if user.is_confirmed == False:
                user.is_confirmed = True
                user.confirmed_on = datetime.now() 
        if confirmation == 'False':
            if user.is_confirmed == True:
                user.is_confirmed = False
                user.confirmed_on = None

        # Role
        role = request.form.get('role')
        if role != user.role:
            user.role = role

        db.session.commit()
        flash("User edited successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/edit-user.html', name=user.name, username=user.username, 
                           email_address=user.email_address, is_confirmed=user.is_confirmed, role=user.role, id=user.id)

@app.route('/admin/user/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_delete_page(id):
    form = SubmitForm()
    user = User.query.get(id)
    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/delete-user.html', form=form, user=user)

@app.route('/admin/products', methods=['GET','POST'])
@admin_required
def admin_products_page():
    products = Product.query.all()
    return render_template('Admin/products.html', products=products)

# For developer purposes

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt')


# Error pages

@app.errorhandler(400)
def page_not_found(e):
    return "Bad Request", 400

@app.errorhandler(403)
def page_not_found(e):
    return render_template('Error/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('Error/404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
