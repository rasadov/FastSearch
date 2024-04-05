"""
This module contains routes for serving static files and handling other miscellaneous requests.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `robots.txt` : Serves the robots.txt file for web crawlers
- `favicon.ico` : Serves the favicon.ico file for the website
"""

from app import app, send_from_directory, os

@app.get("/favicon.ico")
def favicon():
    """
    Endpoint for serving the favicon.ico file.

    Returns:
        The favicon.ico file as a response.
    """
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "images/favicon/favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.get("/robots.txt")
def robots():
    """
    Returns the content of the 'robots.txt' file.

    This function retrieves the 'robots.txt' file from the 'static' directory
    and returns its content.

    Returns:
        str: The content of the 'robots.txt' file.
    """
    return send_from_directory(os.path.join(app.root_path, "static"), "robots.txt")
