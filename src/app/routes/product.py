from datetime import timedelta
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

# Subcribtions

@app.route('/subcribe/monthly', methods=['GET', 'POST'])
@login_required
def subcribe_monthly():
    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=30)
    flash('Subcribed successfully for 1 month', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))

@app.route('/subcribe/quarterly', methods=['GET', 'POST'])
@login_required
def subcribe_quarterly():
    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=90)
    flash('Subcribed successfully for 3 months', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))

@app.route('/subcribe/yearly', methods=['GET', 'POST'])
@login_required
def subcribe_yearly():
    user = User.query.get(current_user.id)
    user.subscribed_till = datetime.now() + timedelta(days=365)
    flash('Subcribed successfully for 1 year', category='success')
    db.session.commit()
    return redirect(url_for('search', query='', page=1))