"""
This file contains the main web application and its configuration.
~~~~~~~~~~~~~~~~~~~~~

All commonly imported libraries in routes and main file are defined in this file.

The web application is built using Flask, a micro web framework for Python. It provides the necessary functionality for handling HTTP requests, rendering templates, and managing user authentication.

The following libraries are imported in this file:
- Flask: The main Flask module for creating the web application.
- flash: A module for displaying flash messages to the user.
- redirect: A function for redirecting the user to a different URL.
- render_template: A function for rendering HTML templates.
- request: A module for handling HTTP requests.
- url_for: A function for generating URLs for specific routes.
- send_from_directory: A function for sending files from a directory.
- session: A module for managing user sessions.

- Flask_Bcrypt: A module for encrypting and verifying passwords using bcrypt.
- Flask_Login: A module for managing user authentication and sessions.
- Flask_SQLAlchemy: A module for integrating SQLAlchemy, an Object-Relational Mapping (ORM) library, with Flask.
- OAuth: A module for integrating OAuth authentication with Flask.
- URLSafeTimedSerializer: A module for generating and verifying URL-safe timed signatures.

- forms: A module containing the forms used in the web application.
- email_sender: A module for sending emails.

- dotenv: A module for loading environment variables from a .env file.
- os: A module for interacting with the operating system.
- datetime: A module for working with dates and times.
- timedelta: A module for representing time intervals.
- randint: A function for generating random integers.
- sys: A module for interacting with the Python interpreter.

The web application uses a PostgreSQL database for storing user data. The database connection details are read from environment variables using the dotenv module.

The web application also integrates with Google OAuth for user authentication. The client ID and client secret are read from environment variables.

The web application defines several decorators for handling user authentication and authorization:
- login_required: A decorator that requires the user to be authenticated.
- logout_required: A decorator that requires the user to be logged out.
- admin_required: A decorator that requires the user to have the "admin" or "owner" role.
- owner_required: A decorator that requires the user to have the "owner" role.
- confirmed_required: A decorator that requires the user to have confirmed their email address.
- unconfirmed_required: A decorator that requires the user to have not confirmed their email address.
- subscribed_required: A decorator that requires the user to be subscribed.

These decorators are used in the routes of the web application to control access to certain pages based on the user's authentication and authorization status.

Overall, this file serves as the central configuration file for the web application, importing all necessary modules and defining important variables and decorators.
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
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

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
SERVER_STARTED_ON = datetime.now()


app = Flask(__name__)


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

microsft = oauth.register(
    name="microsoft",
    client_id=os.environ.get("MICROSOFT_CLIENT_ID"),
    client_secret=os.environ.get("MICROSOFT_CLIENT_SECRET"),
    access_token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
    access_token_params=None,
    authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
    authorize_params=None,
    api_base_url="https://graph.microsoft.com/v1.0/",
    userinfo_endpoint="https://graph.microsoft.com/v1.0/me",
    client_kwargs={"scope": "User.Read"},
    sever_metadata_url="https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
)

# facebook = oauth.register(
#     name="facebook",
#     client_id=os.environ.get("FACEBOOK_CLIENT_ID"),
#     client_secret=os.environ.get("FACEBOOK_CLIENT_SECRET"),
#     authorize_url="https://www.facebook.com/v11.0/dialog/oauth",
#     access_token_url="https://graph.facebook.com/v11.0/oauth/access_token",
#     userinfo_endpoint="https://graph.facebook.com/v11.0/me?fields=id,name,email",
#     client_kwargs={"scope": "email"},
# )


bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])


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