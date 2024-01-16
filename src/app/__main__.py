from flask import redirect, render_template, url_for, flash, send_from_directory
from flask_login import login_user, logout_user
from web import *
from models import *
from forms import *


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,user_id)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
@app.route('/home')
def home_page():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(username=form.username.data).count():
            if not User.query.filter_by(email_address=form.email_address.data).count():
                user = User(name=form.name.data, username=form.username.data, password=form.password.data, email_address=form.email_address.data)
                # db.create_all()
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for('home_page'))
            else:
                flash('This Email is already used', category='danger')
        else:
            flash('This Username is already taken', category='danger')
    if form.errors != {}: # if there are no errors from validations
        for err_msg in form.errors.values():
            print(f"There was an error: {err_msg[0]}")
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.chech_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            return redirect(url_for('home_page'))
        else:
            flash("Username or password is not correct")




    return render_template("login.html", form=form)


@app.route('/logout', methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for('home_page'))


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Page not found</h1>"



if __name__ == "__main__":
    app.run(debug=True)
