"""
This module imports the routes for the account section of the application.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- GET `/profile`: Retrieve the user's profile and render the profile page.
"""

from .authentication import *

from .settings import *

from .subscription import *

from app.models import Cart


@app.get("/profile")
@login_required
def profile_get():
    """
    Retrieve the user's profile and render the profile page.

    Returns:
        The rendered profile page with the user's cart items.
    """
    cart = Cart.items(current_user.id)
    return render_template("Account/profile.html", cart=cart)
