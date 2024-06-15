"""
This module imports all the main routes for the application.
"""

from flask import Blueprint

import app.routes.main.main

import app.routes.main.other

import app.routes.main.errors

blueprint = Blueprint("main", __name__)

blueprint.register_blueprint(app.routes.main.main.blueprint)
blueprint.register_blueprint(app.routes.main.other.blueprint)
blueprint.register_blueprint(app.routes.main.errors.blueprint)
