"""
This module contains routes for serving static files and handling other miscellaneous requests.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `robots.txt` : Serves the robots.txt file for web crawlers
"""

from web import *


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
    title = request.form["title"]
    subject = request.form["subject"]
    message = request.form["message"]
    if name and title and message:
        send_email(
            "rasadov20309@ada.edu.az",
            f"{name} ({current_user.email_address}) has sent you message: \n\n {message}",
            subject=subject,
            title=f"Abyssara user: {title}",
        )
        flash("Your message has been sent. Thank you!", "success")
    else:
        flash("Please fill out all the fields", "danger")