"""
This module contains routes for serving static files and handling other miscellaneous requests.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `robots.txt` : Serves the robots.txt file for web crawlers
"""

from app import app, send_from_directory, os
from models import User


@app.get("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "images/favicon/favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.get("/robots.txt")
def robots():
    return send_from_directory(os.path.join(app.root_path, "static"), "robots.txt")