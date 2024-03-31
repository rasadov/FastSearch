r"""
This file is the entry point of the application.
It contains the main function that runs the application.
It initializes the routes and configures the application.
~~~~~~~~~~~~~~~~~~~~~

Routes are defined in the folder `routes`.
The routes are divided into different files based on their functionality.:
    Main.py: The main routes of the application. It contains the home page and the search page.
    Account.py: The routes related to the user account. 
    It contains the login, register, logout and account management routes.
    Admin.py: The routes related to the admin panel.
    It contains the admin panel and the admin login routes.
    Other.py: The routes related to other pages.
    It contains the contact and donate pages.
    Errors.py: The routes related to error handling.
    It contains the error handling routes.

Database Models are defined in the `models.py` file.

The web application is initialized in the `web.py` file.

The main function runs the application in debug mode. 
THIS RUNS THE APPLICATION IN DEVELOPMENT MODE. DO NOT USE IN PRODUCTION.
USE A WSGI SERVER LIKE GUNICORN OR UWSGI TO RUN THE APPLICATION IN PRODUCTION.

Roadmap:
- Implement anti-scraping measures in the web application.
  Use AJAX to load the search results like in analytics.py.
- Fix the pagination in the search page for mobile.
- Use Docker to containerize the application.
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

from __init__ import app, db, login_manager
from app.models import User
from app.routes import *




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
    except (ValueError, TypeError):
        return None

# Main function

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
