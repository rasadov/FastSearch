"""
This module imports all the routes for the application.
"""

from flask import Blueprint

from app.routes import main
from app.routes import account
from app.routes import admin

blueprint = Blueprint("routes", __name__)

blueprint.register_blueprint(main.blueprint)
blueprint.register_blueprint(account.blueprint)
blueprint.register_blueprint(admin.blueprint)
