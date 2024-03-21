r"""
This file is the entry point of the application. It contains the main function that runs the application.
It initializes the routes and configures the application.
~~~~~~~~~~~~~~~~~~~~~

Routes are defined in the folder `routes`. The routes are divided into different files based on their functionality.:
    Main.py: The main routes of the application. It contains the home page and the search page.
    Account.py: The routes related to the user account. It contains the login, register, logout and account management routes.
    Admin.py: The routes related to the admin panel. It contains the admin panel and the admin login routes.
    Other.py: The routes related to other pages. It contains the contact and donate pages.
    Errors.py: The routes related to error handling. It contains the error handling routes.

Database Models are defined in the `models.py` file.

The web application is initialized in the `web.py` file.

The main function runs the application in debug mode. 
THIS RUNS THE APPLICATION IN DEVELOPMENT MODE. DO NOT USE IN PRODUCTION.
USE A WSGI SERVER LIKE GUNICORN OR UWSGI TO RUN THE APPLICATION IN PRODUCTION.

Roadmap of remaining work (in order). Estimated time: 2-3 weeks. Start Date: 2024-03-14. Progress: 70%
Roadmap:

- DONE: Test the scraping functionality with the `google` method in the web application side.
- DONE: Add the functionality `Forgot Password` in the `app/routes/account.py` file.
- DONE: Update the Email verification functionality in the `app/routes/account.py` file.
- DONE: Add the functionality to the `app/routes/other.py` file to handle the contact and donate pages.
- DONE: Add filters to the `app/routes/product.py` file to filter products by category, price, and brand.
- DONE: Implement the donation functionality in the `app/routes/other.py` file.
- DONE: Add the functionality to automatically scrape products from the web everyday and update the records in the database.
- DONE: Finish functions to the `spiders/myproject/myproject/spiders/utils.py` file. Functions: `scrape_ebay`, `scrape_amazon_uk`.
- DONE: Work on the `app/routes/product.py` file to implement the price history.
- DONE: Implement OAuth2.0 with Microsoft in the `app/routes/account.py` file.
- DONE: Use Google Analytics to track user interactions.
- DONE: Improve search functionality in the `app/routes/product.py` file.
- DONE: Create Card for user model in the `models.py` file. 

- Work on admin/analytics page to show the data of the web application.
- Implement Card functionality in the application.
- Finish the implementation of the `admin/analysis` route in the `app/routes/admin.py` file.
- Check if google analytics ignores the admin panel and token routes.
- Work on the design and front-end of the routes in the `app/routes/product.py`, `app/routes/account.py` files.
- Use Docker to containerize the application.
- Deploy the application to a cloud platform Microsoft Azure or AWS.

Extra:
- DONE: After implementation of filters in `/search` route, implement the same functionality in the admin panel.
- DONE: Also improve search functionality in the admin panel.

- Implement recommendation system in the web application side.
- Add the chatbot functionality to the web application.

Future Work (After the Roadmap):
- Add new functions in the `spiders/myproject/myproject/spiders/utils.py` file to scrape products from other websites.
- Implement the subscription functionality in the `app/routes/subscription.py` file.

Notes:
- The `app/routes/subscriptions.py` file is not implemented. It is a placeholder for future work.
- Probably during development proccess, the roadmap will change.
- function `scrape_amazon_uk` was removed. amazon.co.uk can be scraped using the `scrape_amazon` function.

"""

from models import User
from web import app, db, login_manager

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))  # noqa: F405
    except (ValueError, TypeError):
        return None


# Routes

from routes import *

# Main function

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
