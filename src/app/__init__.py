import os
from datetime import datetime

import dotenv


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

CURRENT_DOMAIN = os.environ.get("CURRENT_DOMAIN")

SECRET_KEY = os.environ.get("SECRET_KEY")