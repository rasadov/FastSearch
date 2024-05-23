"""
This module imports the routes for the account section of the application.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- GET `/profile`: Retrieve the user's profile and render the profile page.
"""

from app.models import Cart

from .authentication import *

from .settings import *


@app.get("/profile")
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
