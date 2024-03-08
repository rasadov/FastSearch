"""
Routes for managing users and products are defined here.
- The user management page is defined here.
- The product management page is defined here.
- The scrapy spider is runned here.
"""

from web import *

sys.path.append(r'C:\Users\RAUF\Desktop\Github_works\FastSearch\src')

from spiders import *

# Admin page

@app.route('/admin', methods=['GET','POST'])
@admin_required
def admin_page():
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template('Admin/admin.html', count_of_products=count_of_products, count_of_users=count_of_users)


@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_users_page():
    page = request.args.get('page', 1, type=int)
    per_page = 3

    search_query = request.args.get('search', '')

    users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page)
    
    cnt = users.total
    
    total_pages = cnt // per_page if cnt % per_page == 0 else cnt // per_page + 1


    return render_template('Admin/Users/users.html', users=users, total_pages=total_pages,
                            search_query=search_query, page=page)

@app.route('/admin/user/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_info_page(id):
    user = User.query.get(id)
    return render_template('Admin/Users/user-info.html', user=user)

@app.route('/admin/user/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_edit_page(id):
    user = User.query.get(id)
    if request.method == 'POST':

        if user.role == 'owner' and current_user.role != 'owner':
            flash("You can't edit owner", category='danger')
            return redirect('/admin/users')

        # Username, name, email
        username = request.form.get('username')
        name = request.form.get('name')
        email_address = request.form.get('email')

        if username != user.username:
            if User.username_exists(username):
                flash("This username is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.username = username
        if name != user.name:
            user.name = name
        if email_address != user.email_address:
            if User.query.filter_by(email_address=email_address).count():
                flash("This email is already taken", category='danger')
                return redirect(f'/admin/user/edit/{id}')
            user.email_address = email_address
            
        # Confimation
        confirmation = request.form.get('confirmed')
        if confirmation == 'True':
            if not user.is_confirmed():
                user.confirmed_on = str(datetime.now())[:19]
        if confirmation == 'False':
            if user.is_confirmed():
                user.confirmed_on = None

        # Role
        role = request.form.get('role')
        
        if user.is_owner() and not current_user.is_owner():
            flash("You can't change owner role", category='danger')
            return redirect(f'/admin/user/edit/{id}')

        if role != user.role:
            user.role = role

        db.session.commit()
        flash("User edited successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/Users/edit-user.html', name=user.name, username=user.username, 
                           email_address=user.email_address, is_confirmed=user.is_confirmed(), role=user.role, id=user.id)

@app.route('/admin/user/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_delete_page(id):
    form = SubmitForm()
    user = User.query.get(id)
    if form.validate_on_submit():
        if user.is_owner() and not current_user.is_owner():
            flash("You can't delete owner", category='danger')
            return redirect('/admin/users')
        
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/Users/delete-user.html', form=form, user=user)


@app.route('/admin/products', methods=['GET','POST'])
@admin_required
def admin_products_page():
    amount = Product.query.count()
    return render_template('Admin/Products/products.html', amount=amount)

@app.route('/admin/products/search', methods=['GET','POST'])
@admin_required
def admin_products_search_page():
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 3

    products = Product.query.filter(
            (Product.title.ilike(f'%{search_query}%')) |
            (Product.url.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page)

    cnt = products.total
    
    total_pages = cnt // per_page if cnt % per_page == 0 else cnt // per_page + 1

    return render_template('Admin/Products/products-search.html', products=products, total_pages=total_pages,
                            search_query=search_query, page=page)

@app.route('/admin/product/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_info_page(id):
    product = Product.query.get(id)
    return render_template('Admin/Products/product-info.html', product=product)

@app.route('/admin/product/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_edit_page(id):
    product = Product.query.get(id)

    if request.method == 'POST':
        # Title, price, item_class, producer, amount_of_ratings, rating, availability
        title = request.form.get('title')
        price = request.form.get('price')
        item_class = request.form.get('item_class')
        producer = request.form.get('producer')
        amount_of_ratings = request.form.get('amount_of_ratings')
        rating = request.form.get('rating')
        availability = request.form.get('availability')

        if title != product.title:
            product.title = title
        if price != product.price:
            product.price = price
        if item_class != product.item_class:
            product.item_class = item_class
        if producer != product.producer:
            product.producer = producer
        if amount_of_ratings != product.amount_of_ratings:
            product.amount_of_ratings = amount_of_ratings
        if rating != product.rating:
            product.rating = rating
        if availability != product.availability:
            product.availability = availability

        db.session.commit()
        flash("Product edited successfully", category='success')
        return redirect(f'/admin/product/{id}')

    return render_template('Admin/Products/edit-product.html', product=product)

@app.route('/admin/product/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_delete_page(id):
    form = SubmitForm()
    product = Product.query.get(id)
    if form.validate_on_submit():
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully", category='success')
        return redirect('/admin/products')
    return render_template('Admin/Products/delete-product.html', form=form, product=product)

@app.route('/admin/product/add', methods=['GET','POST'])
@admin_required
def admin_product_add_page():
    return render_template('Admin/Products/add-product.html')

@app.route('/admin/product/add/google-search', methods=['GET','POST'])
@admin_required
def admin_product_add_google_search_page():
    url = request.form.get('query')
    
    if request.method == 'POST':
        if not url:
            flash("Enter query", category='danger')
            return redirect('/admin/product/add/google-search')
    
        spider = MySpider(url, 'google')
        spider.run()
        spider.close()
        flash("Function runned successfully", category='success')
        return redirect('/admin/Products/products')
        

    
@app.route('/admin/product/add/manual', methods=['GET','POST'])
@admin_required
def admin_product_add_manual_page():
    url = request.form.get('query')
    

    if request.method == 'POST':
        if not url:
            flash("Enter query", category='danger')
            return redirect('/admin/product/add/manual')
        
        
        product = Product.query.filter_by(url=url)
        if product.count():
            flash("Product already in database", category='info')
            product = product.first()
            return redirect(f'/admin/product/{product.id}')
        
        spider = MySpider(url)

        spider.run()
        spider.close()
        product = Product.query.filter_by(url=url)
        if product.count():
            flash("Product added to database succesfully", category='success')
            return redirect(f'/admin/product/{product.id}')
        else:
            flash("Product could not be added to database", category='danger')
            flash("Check if the URL is correct and supported by our program", category='danger')
            return redirect('/admin/product/add/manual')

    return render_template('Admin/Products/add-product-manual.html')   