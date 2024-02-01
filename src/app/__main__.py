from flask import redirect, render_template, request, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, current_user
from web import *
from models import *
from forms import *


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
    return render_template("index.html")

# Product search page

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = Product.query.filter(Product.title.ilike(f'%{search_query}%')).all()
        return render_template('search_results.html', results=results, query=search_query)

    return render_template('search.html')

# Profile page 

@app.route('/profile', methods=['GET','POST'])
def profile_page():
    return render_template('profile.html')

@app.route('/edit-profile', methods=['GET','POST'])
def edit_profile():
    if current_user.is_anonymous:
        return redirect('/login')
    if request.method == 'POST':
        pass
    return render_template('edit_profile.html')
    
@app.route('/change-password', methods=['GET','POST'])
def change_password():
    if current_user.is_anonymous:
        return redirect('/login')
    form = ChangePasswordForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.chech_password_correction(attempted_password=form.old_password.data):
                current_user.password = form.password.data
                db.session.commit()
                flash("Password changed successfully", category='success')
                return redirect('/')
            else:
                flash("Old password is not correct", category='danger')
    return render_template('change-password.html') # Not working yet

# @app.route('/edit-profile', methods=['GET','POST'])
# def edit_profile():
#     if current_user.is_anonymous:
#         return redirect('/login')
#     if request.method == 'POST':
#         pass
#     return render_template('edit_profile.html')


# Register and login page

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email_address=form.email_address.data).count():
            user = User(password=form.password.data, email_address=form.email_address.data)
            # db.create_all()
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/')
        else:
            flash('This Email is already used', category='danger')
    
    if form.errors != {}: # if there are no errors from validations
        for err_msg in form.errors.values():
            print(f"There was an error: {err_msg[0]}")
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET','POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.chech_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            return redirect('/')
        else:
            flash("Username or password is not correct")

    return render_template("login.html", form=form)
    
@app.route('/login-with-google',methods=['GET','POST'])
def login_with_google():
    if current_user.is_authenticated:
        return redirect('/')
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    if current_user.is_authenticated:
        return redirect('/')
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info

    user_to_add = User(email_address=user['email'], name=user['name'])
    if not user_to_add.user_exists():
        db.session.add(user_to_add)
        db.session.commit()
        login_user(user_to_add)
    else:
        user_to_login = User.query.filter_by(email_address=user_to_add.email_address).first()
        login_user(user_to_login)    
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

# Logout page

@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect('/')

# Error pages

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Page not found</h1>"



if __name__ == "__main__":
    app.run(debug=True)
