"""
This module imports the routes for the account section of the application.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- GET `/profile`: Retrieve the user's profile and render the profile page.
"""

from flask import render_template, flash, Blueprint
from flask_login import current_user

from app.models import Cart
from app.utils.decorators import login_required

import authentication
import settings


blueprint = Blueprint("account", __name__)

blueprint.register_blueprint(authentication.blueprint)
blueprint.register_blueprint(settings.blueprint)

@blueprint.get("/profile")
@login_required
def profile_get():
    """
    Retrieve the user's profile and render the profile page.

    Returns:
        The rendered profile page with the user's cart items.
    """
    cart = Cart.items(current_user.id)
    if not current_user.is_confirmed():
        flash("Please confirm your email address to recieve notifications", "warning")
    return render_template("Account/profile.html", cart=cart)
