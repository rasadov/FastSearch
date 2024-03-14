r"""
This file is the entry point of the application. It contains the main function that runs the application.
It initializes the routes and configures the application.


Roadmap of remaining work (in order). Estimated time: 2-3 weeks. 
Roadmap:

- DONE: Test the scraping functionality with the `google` method in the web application side. 

- Add the functionality `Forgot Password` in the `app/routes/account.py` file.
Partially DONE: functionality added but not tested yet.


- Add the functionality to the `app/routes/other.py` file to handle the contact and about pages.
- Add filters to the `app/routes/product.py` file to filter products by category, price, and brand.
- Implement the `newegg` method in the web application side to scrape products from Newegg and test it.
- Finish functions to the `spiders/myproject/myproject/spiders/utils.py` file.
- Add the functionality to automatically scrape products from the web everyday and update the records in the database.
- Update the Email verification functionality in the `app/routes/account.py` file.
- Work on the design and front-end of the routes in the `app/routes/product.py`, `app/routes/account.py` files.
- Work on the `app/routes/product.py` file to implement the price history graph. Note: Use google charts to implement the graph.
- Implement OAuth2.0 with Microsoft and Facebook in the `app/routes/account.py` file.
- Use Google Analytics to track user interactions.
- Use Docker to containerize the application.
- Deploy the application to a cloud platform Microsoft Azure or AWS.

Extra:
- After implementation of filters in `/search` route, implement the same functionality in the admin panel.
- Add new functions
- Implement recommendation system in the web application side.
- Add the chatbot functionality to the web application.

Future Work (After the Roadmap):
- Implement the subscription functionality in the `app/routes/subscription.py` file.

Notes:
- The `app/routes/subscriptions.py` file is not implemented. It is a placeholder for future work.
- Probably during development proccess, the roadmap will change.
"""

from web import *
from models import *


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User,int(user_id))
    except (ValueError, TypeError):
        return None 

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')

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
