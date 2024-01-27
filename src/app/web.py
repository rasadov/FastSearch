from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import dotenv
import os

dotenv.load_dotenv()

DB_URL = os.environ.get('DB_URL')

app = Flask(__name__)
oauth = OAuth(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)
# with app.app_context():
#     db.create_all()

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

from flask import session
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and usethe user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return 'You aint logged in, no page for u!'
    return decorated_function

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'