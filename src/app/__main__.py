r"""
This file is the entry point of the application. It contains the main function that runs the application.
It initializes the routes and configures the application.



Roadmap of remaining work (in order):

- Scraping functionality in admin panel with `google` method is working but gives an error. Handle the error and fix the functionality:
2024-03-14 11:44:08 [scrapy.core.scraper] ERROR: Spider error processing <GET https://www.amazon.com/rtx-3060-mini/s?k=rtx+3060+mini> (referer: None)
Traceback (most recent call last):
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\.venv\Lib\site-packages\twisted\internet\defer.py", line 892, in _runCallbacks
    current.result = callback(  # type: ignore[misc]
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\src\spiders\myproject\myproject\spiders\__init__.py", line 71, in parse
    parsing_method(response)
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\src\spiders\myproject\myproject\spiders\utils.py", line 448, in parsing_method
    scrape_amazon_item(response, url)
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\src\spiders\myproject\myproject\spiders\utils.py", line 276, in scrape_amazon_item
    flash(f"Error: {e}", "danger")
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\.venv\Lib\site-packages\flask\helpers.py", line 323, in flash
    flashes = session.get("_flashes", [])
              ^^^^^^^^^^^
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\.venv\Lib\site-packages\werkzeug\local.py", line 311, in __get__
    obj = instance._get_current_object()
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\RAUF\Desktop\Github_works\FastSearch\.venv\Lib\site-packages\werkzeug\local.py", line 508, in _get_current_object
    raise RuntimeError(unbound_message) from None
RuntimeError: Working outside of request context.

This typically means that you attempted to use functionality that needed
an active HTTP request. Consult the documentation on testing for
information about how to avoid this problem.


- Add the functionality `Forgot Password` in the `app/routes/account.py` file.
- Add the functionality to the `app/routes/other.py` file to handle the contact and about pages.
- Finish and add new functions to the `spiders/myproject/myproject/spiders/utils.py` file.
- Add the functionality to automatically scrape products from the web everyday and update the records in the database.
- Update the Email verification functionality in the `app/routes/account.py` file.
- Work on the design and front-end of the routes in the `app/routes/product.py`, `app/routes/account.py` files.
- Work on the `app/routes/product.py` file to implement the price history graph. Note: Use google charts to implement the graph.
- Implement OAuth2.0 with Microsoft and Facebook in the `app/routes/account.py` file.
- Use Google Analytics to track user interactions.
- Use Docker to containerize the application.
- Deploy the application to a cloud platform Microsoft Azure or AWS.

Extra:
- Implement the `newegg` method in the web application side to scrape products from Newegg and test it.
- Implement recommendation system in the web application side.
- Add the chatbot functionality to the web application.

Future Work (After the Roadmap):
- Implement the subscription functionality in the `app/routes/subscription.py` file.

Notes:
- The `app/routes/subscriptions.py` file is not implemented. It is a placeholder for future work.
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
