"""
The routes related to subscription are defined here
~~~~~~~~~~~~~~~~~~~~~

All payment related proccesses are handled here 

Note: This file is not implemented. It is a placeholder for future work.

Routes:
- `/subcribe/<int:period>`: Subscribes the user for 1 month.
"""

from models import User
from web import app, db, current_user, redirect, url_for, flash, request, datetime, timedelta


def subscribe(days: int = 0, user: User = current_user):
    """
    Subscribes a user for a specified number of days.

    Args:
        days (int): The number of days to subscribe the user for. Default is 0.
        user (User): The user to subscribe. Default is the current user.

    Returns:
        None

    """
    if user.subscribed_till is None or user.subscribed_till < datetime.now():
        date = datetime.now().date()
    else:
        date = user.subscribed_till

    user.subscribed_till = date + timedelta(days=days)
    db.session.commit()


    return redirect(url_for("search_get", query="", page=1))

@app.route("/subcribe", methods=["GET", "POST"])
def subscribe_page():
    """
    Not Finished
    ~~~~~~~~~~~
    This route is used to subscribe the user. Placeholder for future work.

    Roadmap:
    - Configure payment gateway
    - Create Template for payment page
    - Implement payment page
    - Implement payment processing
    - Implement subscription with three options: 1 month, 3 months, 1 year

    Args:
        period (int): The number of days to subscribe the user for.

    Returns:
        None
    """

    period = request.args.get("period", 30, type=int)

    if current_user.is_anonymous:
        flash("You need to login to subscribe", category="info")
        return redirect(url_for("login_get"))

    # Add your code below

    subscribe(period)
    flash("Subcribed successfully for 1 month", category="success")
    db.session.commit()
    return redirect(url_for("search_get", query="", page=1))
