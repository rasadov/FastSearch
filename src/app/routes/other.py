"""
Routes for other pages.

Routes:
- `robots.txt` : Serves the robots.txt file for web crawlers
"""

from web import *

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt')

