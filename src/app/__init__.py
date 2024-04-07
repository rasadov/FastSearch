"""
This file contains the main web application and its configuration.
~~~~~~~~~~~~~~~~~~~~~

All commonly imported libraries in routes and main file are defined in this file.

The web application is built using Flask, a micro web framework for Python. 
It provides the necessary functionality for handling HTTP requests, 
rendering templates, and managing user authentication.

The following libraries are imported in this file:
----------------
- os: A module for interacting with the operating system.
- datetime: A module for working with dates and times.
- wraps: A function for creating well-behaved decorators.

- dotenv: A module for loading environment variables from a .env file.
- Flask: The main Flask module for creating the web application.
- Flask_Bcrypt: A module for encrypting and verifying passwords using bcrypt.
- Flask_Login: A module for managing user authentication and sessions.
- Flask_SQLAlchemy: A module for integrating SQLAlchemy, 
an Object-Relational Mapping (ORM) library, with Flask.
- OAuth: A module for integrating OAuth authentication with Flask.
- authlib: A module for integrating OAuth with Flask.
- URLSafeTimedSerializer: A module for generating and verifying URL-safe timed signatures.
- itsdangerous: A module for generating and verifying cryptographically signed tokens.



The web application uses a PostgreSQL database for storing user data. 
The database connection details are read from environment variables using the dotenv module.

The web application also integrates with Google OAuth for user authentication. 
The client ID and client secret are read from environment variables.

The Bcrypt module is used for encrypting and verifying user passwords.

The LoginManager module is used for managing user authentication and sessions.

The SQLAlchemy module is used for integrating SQLAlchemy with Flask.

The URLSafeTimedSerializer module is used for generating and verifying URL-safe timed signatures.

The web application defines several variables for configuration:
----------------
- app: The main Flask application.
- SECRET_KEY: A secret key used for encrypting session data.
- SQLALCHEMY_DATABASE_URI: The URI for connecting to the PostgreSQL database.
- db: The SQLAlchemy database instance.
- oauth: The OAuth instance for integrating OAuth with Flask.
- google: The OAuth provider for Google authentication.
- microsoft: The OAuth provider for Microsoft authentication.
- bcrypt: The Bcrypt instance for encrypting and verifying passwords.
- login_manager: The LoginManager instance for managing user authentication and sessions.
- s: The URLSafeTimedSerializer instance for generating and verifying URL-safe timed signatures.
- DB_USER: The username for connecting to the PostgreSQL database.
- DB_NAME: The name of the PostgreSQL database.
- DB_PASSWORD: The password for connecting to the PostgreSQL database.
- DB_HOST: The host address of the PostgreSQL database.
- DB_PORT: The port number of the PostgreSQL database.
- SERVER_STARTED_ON: The date and time when the server was started.
- OWNER_EMAIL: The email address of the owner of the web application.
- OWNER_USERNAME: The username of the owner of the web application.
- DONATION_LINK: A link to donate to the web application.

The web application defines several decorators for handling user authentication and authorization:
----------------
- login_required: A decorator that requires the user to be authenticated.
- logout_required: A decorator that requires the user to be logged out.
- admin_required: A decorator that requires the user to have the "admin" or "owner" role.
- owner_required: A decorator that requires the user to have the "owner" role.
- confirmed_required: A decorator that requires the user to have confirmed email address.
- unconfirmed_required: A decorator that requires the user to have unconfirmed email address.
- subscribed_required: A decorator that requires the user to be subscribed.

These decorators are used in the routes of the web application to control 
access to certain pages based on the user's authentication and authorization status.

Overall, this file serves as the central configuration file for the web application, 
importing all necessary modules and defining important variables and decorators.
"""

import os
from datetime import datetime
from functools import wraps

import dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

dotenv.load_dotenv('envs\\flask\\.env')
dotenv.load_dotenv('envs\\postgresql\\.env')

DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
SERVER_STARTED_ON = datetime.now()

OWNER_EMAIL = os.environ.get("OWNER_EMAIL")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME")

DONATION_LINK = "https://www.buymeacoffee.com/abyssara"

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
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
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    # Parameter above is only needed if using openId to fetch user info
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
    sever_metadata_url=
    "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration",
)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

s = URLSafeTimedSerializer(app.config["SECRET_KEY"])

def login_required(f):
    """
    Decorator function to require login for a route.

    This function is used as a decorator to protect routes that require authentication.
    If the current user is not authenticated, they will be redirected to the login page.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            flash("You are not authenticated.", "info")
            return redirect(url_for("login_get"))
        return f(*args, **kwargs)

    return decorated_function


def logout_required(f):
    """
    Decorator function to require logout before accessing a route.

    This decorator checks if the current user is already authenticated.
    If the user is authenticated,
    a flash message is displayed and the user is redirected to the home page. 
    Otherwise, the original function is called.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator function to restrict access to admin-only views.

    This decorator checks if the current user is authenticated and
    has the role of "admin" or "owner".
    If the user is not authorized,
    they are redirected to the home page with a flash message.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or (
            current_user.role not in ["admin", "owner"]
        ):
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def owner_required(f):
    """
    Decorator function that checks if the current user is an owner.
    If the user is not authorized, it flashes a message and redirects to the home page.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or current_user.role != "owner":
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def confirmed_required(f):
    """
    Decorator function to require user confirmation.

    This decorator checks if the current user has confirmed their email address.
    If the user has not confirmed their email, a flash message is displayed and
    the user is redirected to the home page.

    Args:
        f: The function to be decorated.

    Returns:
        The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_confirmed():
            flash("You need to confirm your email address.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def unconfirmed_required(f):
    """
    Decorator function that checks if the current user is confirmed.
    If the user is already confirmed, it flashes a message and redirects to the home page.
    Otherwise, it calls the decorated function.

    Args:
        f: The function to be decorated.

    Returns:
        The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_confirmed():
            flash("You are already confirmed.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def subscribed_required(f):
    """
    Decorator function to require subscription for accessing a page.

    This decorator checks if the current user is subscribed. If not, it displays a flash message
    indicating that the user needs to subscribe and redirects them to the home page.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_subscribed():
            flash("You need to subscribe to access this page.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function
