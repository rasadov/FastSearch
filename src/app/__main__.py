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

Roadmap:
- Deploy the application to a cloud platform Microsoft Azure or AWS.

Extra:
- Implement recommendation system in the web application side.
- Add the chatbot functionality to the web application.

Future Work (After the Roadmap):
- Add new functions in the `spiders/myproject/myproject/spiders/utils.py`
  file to scrape products from other websites.
- Implement the subscription functionality in the `app/routes/subscription.py` file.

Notes:
- The `app/routes/subscriptions.py` file is not implemented. It is a placeholder for future work.
- Probably during development proccess, the roadmap will change.
- function `scrape_amazon_uk` was removed. amazon.co.uk
  can be scraped using the `scrape_amazon` function.
"""

# Import the necessary modules
import sys

sys.path.append("src/")

from app.models import User
from app import app, db, login_manager


# Configure the login manager to load the user
@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database based on the user ID.

    Args:
      user_id (int): The ID of the user to load.

    Returns:
      User or None: The loaded user object if found, None otherwise.
    """
    try:
        return db.session.get(User, int(user_id))  # noqa: F405
    except Exception:
        return None
# Import routes

from app.routes import *

# Main function
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
