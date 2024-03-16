r"""
This file is the entry point of the application. It contains the main function that runs the application.
It initializes the routes and configures the application.
~~~~~~~~~~~~~~~~~~~~~

Roadmap of remaining work (in order). Estimated time: 2-3 weeks. Start Date: 2024-03-14. Progress: 60% 
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

- Implement OAuth2.0 with Facebook in the `app/routes/account.py` file.
- Use Google Analytics to track user interactions.
- Improve search functionality in the `app/routes/product.py` file.
- Work on the design and front-end of the routes in the `app/routes/product.py`, `app/routes/account.py` files.
- Use Docker to containerize the application.
- Deploy the application to a cloud platform Microsoft Azure or AWS.

Extra: 
- DONE: After implementation of filters in `/search` route, implement the same functionality in the admin panel.

- Try to get API for scraping Amazon products. If not possible, in `scrape_amazon` function we access data from html side. In other amazon websites (amazon.co.uk, amazon.de, etc.) check if we can access data from json side. If yes, implement the functionality to scrape products from other amazon websites.
- Also improve search functionality in the admin panel.
- Add new functions in the `spiders/myproject/myproject/spiders/utils.py` file to scrape products from other websites.
- Implement recommendation system in the web application side.
- Add the chatbot functionality to the web application.

Future Work (After the Roadmap):
- Implement the subscription functionality in the `app/routes/subscription.py` file.

Notes:
- The `app/routes/subscriptions.py` file is not implemented. It is a placeholder for future work.
- Probably during development proccess, the roadmap will change.
- function `scrape_amazon_uk` was removed. amazon.co.uk can be scraped using the `scrape_amazon` function.

"""

from web import *
from models import *


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User,int(user_id))
    except (ValueError, TypeError):
        return None 

######## Product pages ########

from routes.product import *

######## User pages ########
    
from routes.account import *

######## Subscription pages ########

from routes.subscription import *

######## Admin pages ########

from routes.admin import *

######## Other pages ########

from routes.other import *

######## Error pages ########

from routes.errors import * 
 
if __name__ == "__main__":
    app.run(debug=True)
