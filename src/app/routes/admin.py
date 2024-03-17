"""
This file contains the routes for the admin panel of the application.
~~~~~~~~~~~~~~~~~~~~~

Routes for managing users and products are defined in this file.
- The user management page is defined in the '/admin/users' route.
- The product management page is defined in the '/admin/products/search' route.
- The scrapy spider can be run by accessing the '/admin/product/add' route.

User Management:
- `/admin/users` route handles the admin user search page, where admin users can search for users in the database.
- `/admin/user/<int:id>` route displays the information of a specific user in the admin panel.
- `/admin/user/edit/<int:id>` route allows editing a user's information in the admin panel.
- `/admin/user/delete/<int:id>` route is used to delete a user from the admin panel.

Product Management:
- `/admin/products/search` route handles the search functionality for admin users to search for products in the database.
- `/admin/product/<int:id>` route displays the information of a specific product in the admin panel.
- `/admin/product/edit/<int:id>` route allows editing a product's information in the admin panel.
- `/admin/product/delete/<int:id>` route is used to delete a product from the admin panel.

Scraping:
- `/admin/product/scrape` route allows running the scrapy spider to scrape product information.
    - The spider can be run by entering the URL of the product manually or by entering a search query to the search engine.

Automatic Scraping:
- The `update_records()` function is used to update the records in the database by scraping products from the web.
- The `scheduler` is used to run the `update_records()` function at regular intervals.

Note:
- All routes require the user to be logged in as an admin.
- Certain actions, such as editing or deleting a user/product, may have additional restrictions based on user roles.
"""

from models import *
from web import *

sys.path.append(r"C:\Users\RAUF\Desktop\Github_works\FastSearch\src")

import atexit
from multiprocessing import Process
from urllib.parse import urlparse

from apscheduler.schedulers.background import BackgroundScheduler

from spiders import *

########## Main admin page.  ##########


@app.get("/admin")
@admin_required
def admin_get():
    """
    This route handles the admin page of the application.

    Returns:
        A rendered template of the admin page with the count of products and users.
    """
    # sample_run_report()
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template(
        "Admin/admin.html",
        count_of_products=count_of_products,
        count_of_users=count_of_users,
    )


########## User management ##########
"""
This section contains routes for managing users.
- User search in database
- User editing, deleting and viewing pages
"""


@app.get("/admin/users")
@admin_required
def admin_user_search_get():
    """
    Renders the admin user search page.

    This route handles the GET request to '/admin/users' and is accessible only to admin users.
    It retrieves the page number and search query from the request arguments.
    It then performs a search query on the User model using the provided search query,
    filtering by username, name, and email address.
    The search results are paginated with a default of 9 items per page.
    The total number of search results and total number of pages are calculated.
    Finally, the search results, total pages, search query, page number, data type, and function name
    are passed to the 'Admin/search.html' template for rendering.

    Returns:
        A rendered template for the admin user search page.
    """

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    users = User.query.filter(
        User.username.ilike(f"%{search}%")
        | User.email_address.ilike(f"%{search}%")
        | User.name.ilike(f"%{search}%")
    )
    variables = {"search": search}

    users = users.paginate(page=page, per_page=9)

    total_pages = users.pages

    return render_template(
        "Admin/search.html",
        items=users,
        total_pages=total_pages,
        variables=variables,
        page=page,
        data_type="User",
        function="admin_user_search_get",
    )


@app.get("/admin/user/<int:id>")
@admin_required
def admin_user_info_get(id):
    """
    This route handles the admin user info page.

    Parameters:
    - id (int): The ID of the user.

    Returns:
    - render_template: The rendered template for the admin user info page.

    Raises:
    - None

    Usage:
    - This route is used to display the information of a specific user in the admin panel.
    - It requires the user to be logged in as an admin.
    - The user ID is passed as a parameter in the URL.
    """
    user = User.query.get(id)
    return render_template("Admin/Item/info.html", item=user)


@app.get("/admin/user/edit/<int:id>")
@admin_required
def admin_user_edit_get(id):
    """
    returns the admin user edit page.

    Args:
        id (int): The ID of the user to be edited.

    Returns:
        Renders the 'Admin/Item/edit.html' template with the user and data_type as context variables.
    """
    user = User.query.get(id)

    return render_template("Admin/Item/edit.html", user=user, data_type="User")


@app.post("/admin/user/edit/<int:id>")
def admin_user_edit_post(id):
    """
    Edits a user with the given ID.

    Args:
        id (int): The ID of the user to be edited.


    Returns:
        - Updates the user's fields based on the form data.
        - Validates the form data using the specified validators.
        - If validation fails, flashes an error message and redirects to the edit page.
        - If validation succeeds, commits the changes to the database, flashes a success message, and redirects to the users page.
    """
    user = User.query.get(id)

    if user.role == "owner" and current_user.role != "owner":
        flash("You can't edit owner", category="danger")
        return redirect("/admin/users")

    fields = {
        "username": {
            "validator": User.username_exists,
            "error_message": "This username is already taken",
        },
        "name": {},
        "email_address": {
            "validator": lambda email: User.query.filter_by(
                email_address=email
            ).count(),
            "error_message": "This email is already taken",
        },
        "confirmed": {},
        "role": {},
    }

    for field, options in fields.items():
        value = request.form.get(field)
        if field == "confirmed":
            if value != f"{user.is_confirmed()}":
                user.confirmed_on = datetime.now().date() if value == "True" else None
            continue
        if getattr(user, field) != value:
            if value == "None":
                value = None

            if "validator" in options and options["validator"](value):
                flash(options["error_message"], category="danger")
                return redirect(f"/admin/user/edit/{id}")
            setattr(user, field, value)

    db.session.commit()
    flash("User edited successfully", category="success")
    return redirect("/admin/users")


@app.get("/admin/user/delete/<int:id>")
@admin_required
def admin_user_delete_get(id):
    """
    This route is used to delete a user with the specified ID from the admin panel.

    Args:
    - id (int): The ID of the user to be deleted.

    Returns:
        - Renders the 'Admin/Item/delete.html' template with the user object and the function name.
    """
    user = User.query.get(id)

    return render_template(
        "Admin/Item/delete.html", item=user, func="admin_user_delete_post"
    )


@app.post("/admin/user/delete/<int:id>")
@admin_required
def admin_user_delete_post(id):
    """
    Deletes a user with the specified ID from the admin panel.

    Args:
        - id (int): The ID of the user to be deleted.

    Returns:
        - Deletes the user from the database.
        - Flashes a success message.
        - Redirects to the '/admin/users' route.

    Note:
        - If the user to be deleted has the role 'owner' and the current user does not have the role 'owner',
        a danger flash message is flashed and the user is redirected to the '/admin/users' route.

    """
    if user.role == "owner" and current_user.role != "owner":
        flash("You can't edit owner", category="danger")
        return redirect("/admin/users")

    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully", category="success")
    return redirect("/admin/users")


########## Product management ##########
"""
This section contains routes for managing products.
- Product search in database
- Product editing, deleting and viewing pages
"""


@app.get("/admin/products/search")
@admin_required
def admin_products_search_get():
    """
    This route handles the search functionality for admin users to search for products.

    Parameters:
    - search (str, optional): The search query to filter products by title.
    - min_price (int, optional): The minimum price to filter products by.
    - max_price (int, optional): The maximum price to filter products by.
    - brand (str, optional): The brand name to filter products by.
    - min_rating (float, optional): The minimum rating to filter products by.
    - max_rating (float, optional): The maximum rating to filter products by.

    Returns:
    - render_template: A Flask function that renders a template with the following arguments:
        - items: The paginated products matching the search filters.
        - total_pages: The total number of pages for the paginated products.
        - variables: A dictionary containing the search filters and their corresponding values.
        - data_type: A string indicating the type of data being searched (in this case, 'Product').
        - function: A string indicating the name of the current function ('admin_products_search_get').
        - page: The current page number for the paginated products.

    Example Usage:
    - When a user visits the '/admin/products/search' route, this function is called to handle the search functionality for admin users.
    - The function retrieves the search filters from the request arguments and applies them to the Product query.
    - The filtered products are then paginated and rendered in the 'Admin/search.html' template along with other necessary data.

    Note:
    - This function requires the user to be an admin, as indicated by the @admin_required decorator.
    """
    page = request.args.get("page", 1, type=int)

    filters = Product.get_filters()

    products = Product.query
    variables = {}
    for key, value in filters.items():
        if value[0]:
            products = value[1](value[0], products)
            variables[key] = value[0]

    products = products.paginate(page=page, per_page=9)

    total_pages = products.pages

    return render_template(
        "Admin/search.html",
        items=products,
        total_pages=total_pages,
        variables=variables,
        data_type="Product",
        function="admin_products_search_get",
        page=page,
    )


@app.get("/admin/product/<int:id>")
@admin_required
def admin_product_info_get(id):
    """
    This route handles the admin product information page.

    Parameters:
    - id (int): The ID of the product.

    Returns:
    - render_template: The rendered template for the admin product information page.

    Raises:
    - None.

    Usage:
    - This route is used to display the information of a specific product in the admin panel.
    - It requires the user to be an admin.

    Example:
    - To access the information page of a product with ID 123, the URL would be '/admin/product/123'.
    """
    product = Product.query.get(id)
    return render_template("Admin/Item/info.html", item=product)


@app.get("/admin/product/edit/<int:id>")
@admin_required
def admin_product_edit_get(id):
    """
    Renders the admin product edit page.

    Args:
        id (int): The ID of the product to be edited.

    Returns:
        A rendered template of the admin product edit page with the product data.

    """
    product = Product.query.get(id)

    return render_template("Admin/Item/edit.html", product=product, data_type="Product")


@app.post("/admin/product/edit/<int:id>")
@admin_required
def admin_product_edit_post(id):
    """
    Edit a product with the given ID.

    Args:
        id (int): The ID of the product to be edited.

    Returns:
        redirect: A redirect to the product details page after successful editing.

    Raises:
        None

    """
    # Title, price, item_class, producer, amount_of_ratings, rating, availability
    fields = [
        "title",
        "price",
        "item_class",
        "producer",
        "amount_of_ratings",
        "rating",
        "availability",
    ]
    product = Product.query.get(id)
    for field in fields:
        value = request.form.get(field)
        if field == "availability":
            # Not finished
            continue

        if getattr(product, field) != value:
            if field == "price":
                price_history = PriceHistory(product_id=id)
                price_history = PriceHistory(id, value, datetime.now().date())
                db.session.add(price_history)
            setattr(product, field, value)

    db.session.commit()
    flash("Product edited successfully", category="success")
    return redirect(f"/admin/product/{id}")


@app.get("/admin/product/delete/<int:id>")
@admin_required
def admin_product_delete_get(id):
    """
    Renders the delete page for a specific product in the admin panel.

    Args:
        id (int): The ID of the product to be deleted.

    Returns:
        - Renders the 'Admin/Item/delete.html' template with the product information and the function name.

    """
    product = Product.query.get(id)
    return render_template(
        "Admin/Item/delete.html", item=product, func="admin_product_delete_post"
    )


@app.post("/admin/product/delete/<int:id>")
@admin_required
def admin_product_delete_post(id):
    """
    Delete a product and its associated price history from the database.

    Args:
        id (int): The ID of the product to be deleted.

    Returns:
        redirect: A redirect response to the admin search page.

    """
    product = Product.query.get(id)
    price_history = PriceHistory.query.filter_by(product_id=id)
    for price in price_history:
        db.session.delete(price)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted successfully", category="success")
    return redirect("/admin/search")


########## Scraping ##########
"""
This section contains routes for running the scrapy spider.
- The spider can be runned by entering the URL of the product manually.
- The spider can be runned by entering the query to the search engine.
"""


def run_spider(url, method=None, pages=None, results_per_page=None):
    """
    Runs a spider to scrape data from a given URL.

    Args:
        url (str): The URL to scrape data from.
        method (str, optional): The HTTP method to use for the request. Defaults to None.
        pages (int, optional): The number of pages to scrape. Defaults to None.
        results_per_page (int, optional): The number of results to scrape per page. Defaults to None.

    Returns:
        None
    """
    spider = MySpider(url, method, pages, results_per_page)
    spider.run()


@app.get("/admin/product/scrape")
@admin_required
def admin_scrape_get():
    """
    Renders the 'Admin/Scraping/add.html' template.
    """

    return render_template("Admin/Scraping/add.html")


@app.post("/admin/product/scrape")
@admin_required
def admin_scrape_post():
    """
    Scrapes the product information from the provided URL and adds it to the database.

    This function is a route handler for the '/admin/product/scrape' endpoint. It is triggered when a POST request is made to the endpoint.
    The function first checks the 'source' parameter in the request form to determine the scraping method.

    If the method is 'custom', it retrieves the 'query' parameter from the form and validates it. If the URL is valid, it checks if the product already exists in the database. If it does, it redirects to the product details page. If not, it starts a new process to run the spider for scraping the product information from the URL. After the process completes, it checks if the product was successfully added to the database and redirects accordingly.

    If the method is 'google', it retrieves the 'query', 'pages', and 'results_per_page' parameters from the form. It validates the 'query' parameter and starts a new process to run the spider for scraping the product information from Google search results. After the process completes, it displays a success message and redirects to the product listing page.

    Returns:
        If the product is added successfully, redirects to the product details page.
        If the product already exists in the database, redirects to the existing product details page.
        If the product could not be added, redirects back to the add product page with an error message.

    """
    method = request.form.get("source")
    if method == "custom":
        url = request.form.get("query")

        if not url:
            flash("Enter query", category="danger")
            return redirect("/admin/product/add/manual")

        parsed_url = urlparse(url)
        url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        product = Product.query.filter_by(url=url)
        if product.count():
            flash("Product already in database", category="info")
            product = product.first()
            return redirect(f"/admin/product/{product.id}")

        p = Process(target=run_spider, args=(url, "url"))
        p.start()
        p.join()

        product = Product.query.filter_by(url=url)
        if product.count():
            flash("Product added to database successfully", category="success")
            product = product.first()
            return redirect(f"/admin/product/{product.id}")
        else:
            flash("Product could not be added to database", category="danger")
            flash(
                "Check if the URL is correct and supported by our program",
                category="danger",
            )
            return redirect("/admin/product/add")

    elif method == "google":
        url = request.form.get("query")
        pages = request.form.get("pages")
        results_per_page = request.form.get("results_per_page")

        if not url:
            flash("Enter query", category="danger")
            return redirect("/admin/product/add")

        p = Process(
            target=run_spider, args=(url, "google", int(pages), int(results_per_page))
        )
        p.start()
        p.join()

        flash("Function run successfully", category="success")
        return redirect("/admin/Products/products")


########## Automatic scraping ##########
"""
This section contains the code for running the spider automatically at regular intervals.
"""


def update_records():
    """
    Updates the records in the database by scraping products from the web.

    This function retrieves all the products from the database and updates their information
    by scraping the web using a spider. If an exception occurs during the scraping process,
    the function continues to the next product.

    Returns:
        None
    """
    products = Product.query.all()
    for product in products:
        try:
            spider = MySpider(product.url, "url")
            spider.run()
        except Exception:
            continue


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_records, trigger="interval", hours=24)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
