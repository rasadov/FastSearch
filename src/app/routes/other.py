"""
Routes for other files like robots.txt, humans.txt, etc.
"""

from web import *

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt')

