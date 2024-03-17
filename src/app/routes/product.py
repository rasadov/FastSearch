"""
This file contains the routes related to the product.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `/`: Renders the home page.
- `/search`: Renders the product search page. Requires the user to be logged in and subscribed.

Functions:
- `home_get()`: Renders the home page.
- `search_get()`: Renders the search page with filtered products based on the query parameters.
"""

from models import *
from web import *


@app.get("/")
def home_get():
    """
    Renders the home page.

    Returns:
    - Rendered template for the home page.
    """
    # sample_run_report()
    # if current_user.is_anonymous:
    #     user = User.query.filter_by(id=1).first()
    #     login_user(user)
    return render_template("Main/index.html")


@app.get("/search")
def search_get():
    """
    Renders the search page with filtered products based on the query parameters.

    Returns:
        The rendered search page with filtered products.

    Query Parameters:
        - search (str): The search keyword to filter products by title.
        - min_price (int): The minimum price to filter products by.
        - max_price (int): The maximum price to filter products by.
        - brand (str): The brand name to filter products by.
        - min_rating (float): The minimum rating to filter products by.
        - max_rating (float): The maximum rating to filter products by.
        - page (int): The page number to paginate the results.

    Returns:
        - Rendered template for the search page with filtered products.
    """
    products = Product.query

    filters = Product.get_filters()

    variables = {}
    for key, value in filters.items():
        val = value[0]
        if val:
            products = value[1](val, products)
            variables[key] = val

    Product.__ts_vector__.match(f"{request.args.get('search', '')}")

    total_pages = products.pages
    return render_template(
        "Main/search.html", products=products, total_pages=total_pages, **variables
    )
