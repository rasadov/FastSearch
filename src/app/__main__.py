from flask_login import login_user
from flask import redirect, render_template, url_for, request
import requests
from web import *
from models import *
from forms import *


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
@app.route('/home')
def home_page():
    return render_template("index.html")

@app.route('/register', methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            instance = User(username=form.username.data,
                            password=form.password.data,
                            name=form.name.data)
            # db.create_all()
            db.session.add(instance)
            db.session.commit()
            login_user(instance)
            return redirect(url_for('home_page'))
    return render_template("register.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.chech_password_correction(attempted_password=form.password.data):
                login_user(attempted_user)
                return redirect(url_for('home_page'))
    return render_template("login.html", form=form)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Page not found</h1>"



if __name__ == "__main__":
    app.run(debug=True)
