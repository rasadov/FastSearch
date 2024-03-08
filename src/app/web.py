"""
This file contains the main web application and its configuration.

All commonly imported libraries in routes and main file are defined in this file.
"""

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    send_from_directory,
    session
)

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from models import *
from forms import *
from email_sender import send_email

import dotenv
import os

from datetime import datetime, timedelta
from random import randint
import sys

from functools import wraps

dotenv.load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")


app = Flask(__name__)
oauth = OAuth(app)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
db = SQLAlchemy(app)


oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",  # This is only needed if using openId to fetch user info
    client_kwargs={"scope": "email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            flash("You are not authenticated.", "info")
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)

    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or (
            current_user.role != "admin" and current_user.role != "owner"
        ):
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function


def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or current_user.role != "owner":
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function


def confirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_confirmed():
            flash("You need to confirm your email address.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function


def unconfirmed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_confirmed():
            flash("You are already confirmed.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function


def subscribed_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_subscribed():
            flash("You need to subscribe to access this page.", "info")
            return redirect(url_for("home_page"))
        return f(*args, **kwargs)

    return decorated_function