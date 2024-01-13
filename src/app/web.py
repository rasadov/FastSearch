from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

DB_URL = os.environ.get('DB_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'