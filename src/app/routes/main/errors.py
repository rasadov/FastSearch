"""
This module defines error handling routes for handling different HTTP error codes.
~~~~~~~~~~~~~~~~~~~~~

The error handling routes are defined using the `@app.errorhandler`
decorator provided by the `web` module.

The following error handling routes are defined:
- 400 Bad Request: Returns a string representing the error message "Bad Request".
- 403 Forbidden: Returns the rendered template for the `403.html` error page.
- 404 Not Found: Returns the rendered template for the `404.html` error page.
"""

from flask import render_template

from app import app


@app.errorhandler(400)
def bad_request(e):
    """
    Error handler for 400 Bad Request error.

    Parameters:
    - e: The exception object.

    Returns:
    - A string representing the error message "Bad Request".
    """
    return f"Bad Request: \n\n {e}", 400


@app.errorhandler(403)
def forbidden(e):
    """
    Error handler for 403 Forbidden error.

    Parameters:
    - e: The exception object.

    Returns:
    - The rendered template for the 403.html error page.
    """
    return render_template("Error/error.html", num=403, e=e), 403


@app.errorhandler(404)
def page_not_found(e):
    """
    Error handler for 404 Not Found error.

    Parameters:
    - e: The exception object.

    Returns:
    - The rendered template for the 404.html error page.
    """
    return render_template("Error/error.html", num=404, e=e), 404
