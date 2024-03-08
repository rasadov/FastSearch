"""Error handling routes."""

from web import *

@app.errorhandler(400)
def page_not_found(e):
    return "Bad Request", 400

@app.errorhandler(403)
def page_not_found(e):
    return render_template('Error/403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('Error/404.html'), 404



