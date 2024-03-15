"""
This file contains the routes related to the product.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- `/`: Renders the home page.
- `/search`: Renders the product search page. Requires the user to be logged in and subscribed.

Functions:
- `home_page()`: Renders the home page.
- `search_page()`: Renders the search page with filtered products based on the query parameters.
"""
from web import *
from models import *

@app.route('/')
def home_page():
    """
    Renders the home page.

    Returns:
    - Rendered template for the home page.
    """
    if current_user.is_anonymous:
        user = User.query.filter_by(id=1).first()
        login_user(user)
    return render_template("Main/index.html")

@app.route('/search', methods=['GET'])
@login_required
@subscribed_required
def search_page():
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
    filters = {
        "search" : [request.args.get('search', ''), lambda search, query: query.filter(Product.title.ilike(f'%{search}%'))],
        "min_price": [request.args.get('min_price', None, type=int), lambda min_price, query: query.filter(Product.price >= min_price)],
        "max_price": [request.args.get('max_price', None, type=int), lambda max_price, query: query.filter(Product.price <= max_price)],
        "brand": [request.args.get('brand', None), lambda brand, query: query.filter(Product.producer.ilike(f"%{brand}%"))],
        "min_rating": [request.args.get('min_rating', None, type=float), lambda rating, query: query.filter(Product.rating >= rating)],
        "max_rating": [request.args.get('max_rating', None, type=float), lambda rating, query: query.filter(Product.rating <= rating)],
        "page": [request.args.get('page', 1, type=int), lambda page, query: query.paginate(page=page, per_page=9)]
    }

    products = Product.query
    variables = {}
    for key, value in filters.items():
        val = value[0]
        if val:
            products = value[1](val, products)
            variables[key] = val
                        
    total_pages = products.pages
    return render_template('Main/search.html', products=products,total_pages=total_pages, **variables)
