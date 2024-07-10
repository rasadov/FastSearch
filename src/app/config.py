"""
This file contains the main web application and its configuration.
~~~~~~~~~~~~~~~~~~~~~

All commonly imported libraries in routes and main file are defined in this file.

The web application is built using Flask, a micro web framework for Python. 
It provides the necessary functionality for handling HTTP requests, 
rendering templates, and managing user authentication.

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


Overall, this file serves as the central configuration file for the web application, 
importing all necessary modules and defining important variables and decorators.
"""

import os

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

from app import DB_USER, DB_NAME, DB_PASSWORD, DB_HOST, DB_PORT, SECRET_KEY


application = Flask(__name__)


application.config["SECRET_KEY"] = SECRET_KEY

application.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
db = SQLAlchemy(application)

oauth = OAuth(application)

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

bcrypt = Bcrypt(application)

login_manager = LoginManager(application)
login_manager.login_view = "login"

s = URLSafeTimedSerializer(application.config["SECRET_KEY"])
