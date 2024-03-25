"""
This module contains routes for serving static files and handling other miscellaneous requests.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `robots.txt` : Serves the robots.txt file for web crawlers
"""

from web import (app, render_template, send_from_directory,
                request, flash, redirect, url_for,
                current_user, send_email, os)
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


@app.get("/donate")
def donation_get():
    return render_template("Main/donate.html")


@app.get("/contact")
def contact_get():
    return render_template("Main/contact.html")

@app.post("/contact")
def contact_post():
    if current_user.is_anonymous:
        flash("You need to be logged in to send a message", "danger")
        return redirect(url_for("login"))
    name = request.form["name"]
    number = request.form["number"] 
    subject = request.form["subject"]
    message = request.form["message"]
    if name and message:
        users = User.query.filter(User.role == "admin" | User.role == "owner").all()
        for user in users:
            send_email(
            user.email_address,
            f"{name} ({current_user.email_address} | {number if number else 'No number'}) has sent you message: \n\n {message}",
            subject=subject,
            title=f"Abyssara user sent you a message",
            )
        flash("Your message has been sent. Thank you!", "success")
    else:
        flash("Please fill out all the fields", "danger")