"""
This file contains the routes related to the product.

Routes:
- `/`: Renders the home page. If the user is anonymous, it logs in a default user.
- `/search`: Renders the product search page. Requires the user to be logged in and subscribed.
"""

from web import *
from models import *

@app.route('/')
def home_page():
    """
    Renders the home page.

    If the user is anonymous, it logs in a default user.

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
    Renders the product search page.

    Requires the user to be logged in and subscribed.

    Query Parameters:
    - search (str): The search query string.
    - page (int): The page number for pagination.

    Returns:
    - Rendered template for the product search page with the search results.
    """
    query = request.args.get('search', '') 
    page = request.args.get('page', 1, type=int)  
    products = Product.query.filter(Product.title.ilike(f'%{query}%')).paginate(page=page, per_page=9)
    total_pages = products.pages
    return render_template('Main/search.html', products=products, query=query, total_pages=total_pages, page=page)
