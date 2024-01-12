from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import dotenv
import os

dotenv.load_dotenv()

user = os.environ.get("DB_USER") 
password = os.environ.get("DB_PASSWORD") 
dbname = os.environ.get("DB_NAME")
host = os.environ.get("HOST_NAME") 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}/{dbname}'
db = SQLAlchemy(app)

@app.route('/')
@app.route('/home')
def home_page():
    return "<h1>Main Page</h1>"


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>Page not found</h1>"

if __name__ == "__main__":
    app.run(debug=True)