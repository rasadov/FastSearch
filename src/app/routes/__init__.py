"""
This module imports all the routes for the application.
"""

from flask import Blueprint

import app.routes.main
import app.routes.account
import app.routes.admin

blueprint = Blueprint("routes", __name__)

blueprint.register_blueprint(app.routes.main.blueprint)
blueprint.register_blueprint(app.routes.account.blueprint)
blueprint.register_blueprint(app.routes.admin.blueprint)
