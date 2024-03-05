from web import *
from models import *

# Home page

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        print(current_user.is_admin())
    return render_template("Main/index.html")

# Product search page

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        results = Product.query.filter(Product.title.ilike(f'%{search_query}%')).all()
        return render_template('Main/search_results.html', results=results, query=search_query)
    if request.method == 'GET':
        return render_template('Main/search.html')