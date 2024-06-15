"""
The web application defines several decorators for handling user authentication and authorization:
----------------
- login_required: A decorator that requires the user to be authenticated.
- logout_required: A decorator that requires the user to be logged out.
- admin_required: A decorator that requires the user to have the "admin" or "owner" role.
- owner_required: A decorator that requires the user to have the "owner" role.
- confirmed_required: A decorator that requires the user to have confirmed email address.
- unconfirmed_required: A decorator that requires the user to have unconfirmed email address.
- subscribed_required: A decorator that requires the user to be subscribed.

These decorators are used in the routes of the web application to control 
access to certain pages based on the user's authentication and authorization status.
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def login_required(f):
    """
    Decorator function to require login for a route.

    This function is used as a decorator to protect routes that require authentication.
    If the current user is not authenticated, they will be redirected to the login page.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            flash("You are not authenticated.", "info")
            return redirect(url_for("login_get"))
        return f(*args, **kwargs)

    return decorated_function


def logout_required(f):
    """
    Decorator function to require logout before accessing a route.

    This decorator checks if the current user is already authenticated.
    If the user is authenticated,
    a flash message is displayed and the user is redirected to the home page. 
    Otherwise, the original function is called.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator function to restrict access to admin-only views.

    This decorator checks if the current user is authenticated and
    has the role of "admin" or "owner".
    If the user is not authorized,
    they are redirected to the home page with a flash message.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or (
            current_user.role not in ["admin", "owner"]
        ):
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def owner_required(f):
    """
    Decorator function that checks if the current user is an owner.
    If the user is not authorized, it flashes a message and redirects to the home page.

    Args:
        f (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous or current_user.role != "owner":
            flash("You are not authorized to view this page.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def confirmed_required(f):
    """
    Decorator function to require user confirmation.

    This decorator checks if the current user has confirmed their email address.
    If the user has not confirmed their email, a flash message is displayed and
    the user is redirected to the home page.

    Args:
        f: The function to be decorated.

    Returns:
        The decorated function.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_confirmed():
            flash("You need to confirm your email address.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function


def unconfirmed_required(f):
    """
    Decorator function that checks if the current user is confirmed.
    If the user is already confirmed, it flashes a message and redirects to the home page.
    Otherwise, it calls the decorated function.

    Args:
        f: The function to be decorated.

    Returns:
        The decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_confirmed():
            flash("You are already confirmed.", "info")
            return redirect(url_for("home_get"))
        return f(*args, **kwargs)

    return decorated_function
