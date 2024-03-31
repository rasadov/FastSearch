"""
This file contains the routes for the admin panel of the application.
~~~~~~~~~~~~~~~~~~~~~

Routes for managing users and products are defined in this file.
- The user management page is defined in the '/admin/users' route.
- The product management page is defined in the '/admin/products/search' route.
- The scrapy spider can be run by accessing the '/admin/product/add' route.

User Management:
- `/admin/users` route handles the admin user search page,
where admin users can search for users in the database.
- `/admin/user/<int:id>` route displays the information of a specific user in the admin panel.
- `/admin/user/edit/<int:id>` route allows editing a user's information in the admin panel.
- `/admin/user/delete/<int:id>` route is used to delete a user from the admin panel.

Product Management:
- `/admin/products/search` route handles the search functionality
for admin users to search for products in the database.
- `/admin/product/<int:id>` route displays the information of a specific product in the admin panel.
- `/admin/product/edit/<int:id>` route allows editing a product's information in the admin panel.
- `/admin/product/delete/<int:id>` route is used to delete a product from the admin panel.

Scraping:
- `/admin/product/scrape` route allows running the scrapy spider to scrape product information.
    - The spider can be run by entering the URL of the
    product manually or by entering a search query to the search engine.

Automatic Scraping:
- The `update_records()` function is used to update the records
  in the database by scraping products from the web.
- The `scheduler` is used to run the `update_records()` function at regular intervals.

Note:
- All routes require the user to be logged in as an admin.
- Certain actions, such as editing or deleting a user/product,
  may have additional restrictions based on user roles.
"""


from app.models import User, Product
from app import app, admin_required, render_template

from app.routes.admin.analytics import *
from app.routes.admin.scrape import *
from app.routes.admin.user import *
from app.routes.admin.product import *
from app.routes.admin.message import *

@app.get("/admin")
@admin_required
def admin_get():
    """
    This route handles the admin page of the application.

    Returns:
        A rendered template of the admin page with the count of products and users.
    """
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template(
        "Admin/admin.html",
        count_of_products=count_of_products,
        count_of_users=count_of_users,
    )
