"""
All the routes related to the product are defined here.
- The home page is defined here.
- The product search page is defined here.
"""

from web import *
from models import *

# Home page

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        print(current_user.is_admin())
    return render_template("Main/index.html")

# Product search page

@app.route('/search', methods=['GET'])
@login_required
@subscribed_required
def search():
    query = request.args.get('search_query', '') 
    page = request.args.get('page', 1, type=int)  
    products = Product.query.filter(Product.title.ilike(f'%{query}%')).paginate(page=page, per_page=10)
    total_pages = products.pages
    return render_template('Main/search.html', products=products, query=query, total_pages=total_pages, page=page)
