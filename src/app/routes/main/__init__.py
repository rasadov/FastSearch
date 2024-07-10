"""
This module imports all the main routes for the application.
"""

from flask import Blueprint

from app.routes.main import main

from app.routes.main import other

from app.routes.main import errors

blueprint = Blueprint("main", __name__)

blueprint.register_blueprint(main.blueprint)
blueprint.register_blueprint(other.blueprint)
blueprint.register_blueprint(errors.blueprint)
