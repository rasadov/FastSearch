r"""
This file is the entry point of the application.
It contains the main function that runs the application.
It initializes the routes and configures the application.
~~~~~~~~~~~~~~~~~~~~~

Routes are defined in the folder `routes`.
The routes are divided into different files based on their functionality.:
    - '/routes/__init__.py': Imports all the routes.

    Account:
    - '/account/__init__.py': imports other account routes.
    - '/account/authentication.py': Contains the routes related to the user's authentication.
    - '/account/profile.py': Contains the routes related to the user's profile.

    Admin:
    - '/admin/__init__.py': Contains main admin page and imports other admin routes.
    - '/admin/analytics.py': Contains the routes related to the analytics page.
    - '/admin/message.py': Contains the routes related to the messages page.
    - '/admin/product.py': Contains the routes related to the products page.
    - '/admin/user.py': Contains the routes related to the users page.
    - '/admin/scrape.py': Contains the routes related to the scraping functionality.

    Main:
    - '/main/main.py': Contains the main routes of the application.
    - '/main/error.py': Contains the error handling routes.
    - '/main/other.py': Contains other routes of the application.

Database Models are defined in the folder `models`.
The models are divided into different files based on their functionality.:
    - '/models/__init__.py': Imports all the models.
    - '/models/user.py': Contains the user model.
    - '/models/product.py': Contains the product model.
    - '/models/message.py': Contains the message model.
    - '/models/cart.py': Contains the cart model.

The web application is initialized in the `__init__.py` file.

The main function runs the application in debug mode. 
THIS RUNS THE APPLICATION IN DEVELOPMENT MODE. DO NOT USE IN PRODUCTION.
USE A WSGI SERVER LIKE GUNICORN OR UWSGI TO RUN THE APPLICATION IN PRODUCTION.
"""

# Import the necessary modules
import sys

sys.path.append("src/")

from app.config import application


# Import routes

import app.routes

application.register_blueprint(app.routes.blueprint)

# Main function
if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=5000)
