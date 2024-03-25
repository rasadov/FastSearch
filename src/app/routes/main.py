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

from flask import jsonify
from models import Product, Cart
from web import (app, render_template, 
            request, redirect, current_user)

from web import login_user
from models import User


@app.get("/")
def home_get():
    """
    Renders the home page.

    Returns:
    - Rendered template for the home page.
    """
    # if current_user.is_anonymous:
    #     login_user(User.query.get(1))
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

    page = request.args.get("page", 1, type=int)
    products = products.paginate(page=page, per_page=9)

    total_pages = products.pages
    return render_template(
        "Main/search.html", products=products, total_pages=total_pages, **variables, in_cart=Cart.in_cart
    )

@app.post('/cart/add')
def add_to_cart():
    """
    Add a product to the user's cart.

    This function handles the POST request to add a product to the user's cart.
    It expects a JSON payload with the following keys:
    - 'product_id': The ID of the product to be added.
    - 'action': The action to be performed, either 'track' or 'remove'.

    If the 'product_id' or 'action' is missing in the payload, it redirects to the homepage ("/").
    If the product exists, it performs the specified action on the user's cart.
    If the action is 'track', it adds the product to the cart.
    If the action is 'remove', it removes the product from the cart.

    Returns:
    - If the action is 'track', it returns a JSON response with status 'success' and action 'track'.
    - If the action is 'remove', it returns a JSON response with status 'success' and action 'remove'.
    - If there is an error, it returns a JSON response with status 'error' and HTTP status code 400.
    """
    
    data = request.get_json()

    if not data['product_id'] or not data['action']:
        return redirect("/")
    product = Product.query.get(data['product_id'])
    
    if product:
        if data['action'] == 'track':
            Cart.append(current_user.id, product.id)
            return jsonify({'status': 'success', 'action': 'track'}), 200
        else:
            Cart.remove(current_user.id, product.id)
            return jsonify({'status': 'success', 'action': 'remove'}), 200
    return jsonify({'status': 'error'}), 400
