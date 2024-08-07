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


from flask import Blueprint, jsonify, render_template

blueprint = Blueprint("admin", __name__)

from app.models import User, Product, Message
from app.utils.decorators import admin_required

from app.routes.admin import analytics
from app.routes.admin import scrape
from app.routes.admin import user
from app.routes.admin import product
from app.routes.admin import message

blueprint.register_blueprint(analytics.blueprint)
blueprint.register_blueprint(scrape.blueprint)
blueprint.register_blueprint(user.blueprint)
blueprint.register_blueprint(product.blueprint)
blueprint.register_blueprint(message.blueprint)

@blueprint.get("/admin")
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


@blueprint.get("/admin/messages/unread")
@admin_required
def get_count_of_messages():
    """
    Retrieves the count of messages in the database.

    Returns:
        int: The count of messages in the database.
    """
    return jsonify({'unread': Message.query.filter_by(read=False).count()})
