"""
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
- `/admin/product/add` route allows running the scrapy spider to scrape product information.
    - The spider can be run by entering the URL of the product manually or by entering a search query to the search engine.

Note:
- All routes require the user to be logged in as an admin.
- Certain actions, such as editing or deleting a user/product, may have additional restrictions based on user roles.
"""

from web import *
from models import *

sys.path.append(r'C:\Users\RAUF\Desktop\Github_works\FastSearch\src')

from spiders import *
from multiprocessing import Process

from urllib.parse import urlparse

########## Main admin page.  ##########

@app.route('/admin', methods=['GET','POST'])
@admin_required
def admin_page():
    """
    This route handles the admin page of the application.

    Returns:
        A rendered template of the admin page with the count of products and users.
    """
    count_of_users = User.query.count()
    count_of_products = Product.query.count()
    return render_template('Admin/admin.html', count_of_products=count_of_products, count_of_users=count_of_users,)

########## User management ##########
"""
This section contains routes for managing users.
- User search in database
- User editing, deleting and viewing pages
"""

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_user_search_page():
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
    page = request.args.get('page', 1, type=int)
    per_page = 9

    search_query = request.args.get('search', '')

    users = User.query.filter(
            (User.username.ilike(f'%{search_query}%')) |
            (User.name.ilike(f'%{search_query}%')) |
            (User.email_address.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page)
    
    cnt = users.total
    
    total_pages = cnt // per_page if cnt % per_page == 0 else cnt // per_page + 1


    return render_template('Admin/search.html', items=users, total_pages=total_pages,
                            search_query=search_query, page=page, data_type='User', function='admin_user_search_page')

@app.route('/admin/user/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_info_page(id):
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
    return render_template('Admin/Item/info.html', item=user)

@app.route('/admin/user/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_edit_page(id):
    """
    This route handles the editing of a user in the admin panel.

    Args:
        id (int): The ID of the user to be edited.

    Returns:
        If the request method is GET:
            Renders the 'Admin/Item/edit.html' template with the user and data_type as context variables.
        If the request method is POST:
            - Updates the user's fields based on the form data.
            - Validates the form data using the specified validators.
            - If validation fails, flashes an error message and redirects to the edit page.
            - If validation succeeds, commits the changes to the database, flashes a success message, and redirects to the users page.
    """
    user = User.query.get(id)
    if user.role == 'owner' and current_user.role != 'owner':
        flash("You can't edit owner", category='danger')
        return redirect('/admin/users')

    if request.method == 'POST':    
        fields = {
            'username': {
                'validator': User.username_exists,
                'error_message': "This username is already taken"
            },
            'name': {},
            'email_address': {
                'validator': lambda email: User.query.filter_by(email_address=email).count(),
                'error_message': "This email is already taken"
            },
            'confirmed': {},
            'role': {}
        }

        for field, options in fields.items():
            value = request.form.get(field)
            if field == 'confirmed':
                if value != f"{user.is_confirmed()}":
                    user.confirmed_on = str(datetime.now())[:19] if value == 'True' else None
                continue
            if getattr(user, field) != value:
                if 'validator' in options and options['validator'](value):
                    flash(options['error_message'], category='danger')
                    return redirect(f'/admin/user/edit/{id}')
                setattr(user, field, value)

        db.session.commit()
        flash("User edited successfully", category='success')
        return redirect('/admin/users')
    
    return render_template('Admin/Item/edit.html', user=user, data_type='User')

@app.route('/admin/user/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_user_delete_page(id):
    """
    This route is used to delete a user with the specified ID from the admin panel.

    Parameters:
    - id (int): The ID of the user to be deleted.

    Returns:
    - If the request method is GET:
        - Renders the 'Admin/Item/delete.html' template with the user object and the function name.
    - If the request method is POST:
        - Deletes the user from the database.
        - Flashes a success message.
        - Redirects to the '/admin/users' route.

    Note:
    - The user must have the 'admin' role to access this route.
    - If the user to be deleted has the role 'owner' and the current user does not have the role 'owner',
      a danger flash message is flashed and the user is redirected to the '/admin/users' route.
    """
    user = User.query.get(id)
    if user.role == 'owner' and current_user.role != 'owner':
        flash("You can't edit owner", category='danger')
        return redirect('/admin/users')
    
    if request.method == 'POST':        
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully", category='success')
        return redirect('/admin/users')
    return render_template('Admin/Item/delete.html', item=user, func='admin_user_delete_page')

########## Product management ##########
"""
This section contains routes for managing products.
- Product search in database
- Product editing, deleting and viewing pages
"""

@app.route('/admin/products/search', methods=['GET','POST'])
@admin_required
def admin_products_search_page():
    """
    This route handles the search functionality for admin users to search for products.

    Parameters:
        search_query (str): The search query entered by the user.
        page (int): The page number for pagination.
        per_page (int): The number of items to display per page.

    Returns:
        render_template: The rendered HTML template for the search results page.

    Raises:
        None
    """
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    products = Product.query.filter(
            (Product.title.ilike(f'%{search_query}%')) |
            (Product.url.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=per_page)

    cnt = products.total

    total_pages = cnt // per_page if cnt % per_page == 0 else cnt // per_page + 1

    return render_template('Admin/search.html', items=products, total_pages=total_pages,
                            search_query=search_query, page=page, data_type='Product', function='admin_products_search_page')

@app.route('/admin/product/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_info_page(id):
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
    return render_template('Admin/Item/info.html', item=product)

@app.route('/admin/product/edit/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_edit_page(id):
    """
    Renders the admin product edit page and handles the form submission for editing a product.

    Args:
        id (int): The ID of the product to be edited.

    Returns:
        If the request method is GET:
            A rendered template of the admin product edit page with the product data.
        If the request method is POST:
            If the product data is successfully edited:
                A redirect to the admin product page for the edited product.
            If the product data is not successfully edited:
                A rendered template of the admin product edit page with an error message.

    """
    product = Product.query.get(id)

    if request.method == 'POST':
        # Title, price, item_class, producer, amount_of_ratings, rating, availability
        fields = ['title', 'price', 'item_class', 'producer', 'amount_of_ratings', 'rating', 'availability']

        for field in fields:
            value = request.form.get(field)
            if field == 'availability':
                # Not finished
                continue

            if getattr(product, field) != value:
                if field == 'price':
                    price_history = PriceHistory(product_id=id)
                    price_history = PriceHistory(id, value, str(datetime.now())[:19])
                    db.session.add(price_history)
                setattr(product, field, value)

        db.session.commit()
        flash("Product edited successfully", category='success')
        return redirect(f'/admin/product/{id}')

    return render_template('Admin/Item/edit.html', product=product, data_type='Product')

@app.route('/admin/product/delete/<int:id>', methods=['GET','POST'])
@admin_required
def admin_product_delete_page(id):
    """
    Renders the delete page for a specific product in the admin panel.

    Args:
        id (int): The ID of the product to be deleted.

    Returns:
        If the request method is POST:
            - Redirects to the '/admin/search' route after deleting the product and its associated price history.
        If the request method is GET:
            - Renders the 'Admin/Item/delete.html' template with the product information and the function name.

    """
    product = Product.query.get(id)
    price_history = PriceHistory.query.filter_by(product_id=id)
    if request.method == 'POST':
        for price in price_history:
            db.session.delete(price)
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully", category='success')
        return redirect('/admin/search')
    return render_template('Admin/Item/delete.html', item=product, func='admin_product_delete_page')


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

@app.route('/admin/product/add', methods=['GET','POST'])
@admin_required
def admin_scrape_page():
    """
    Route for adding a product to the database through scraping.

    GET: Renders the 'Admin/Scraping/add.html' template.
    POST: Scrapes the product information from the provided URL and adds it to the database.

    Returns:
        If the product is added successfully, redirects to the product details page.
        If the product already exists in the database, redirects to the existing product details page.
        If the product could not be added, redirects back to the add product page with an error message.
    """
    if request.method == 'POST':
        method = request.form.get('source')
        if method == 'custom':
            url = request.form.get('query')

            if not url:
                flash("Enter query", category='danger')
                return redirect('/admin/product/add/manual')

            parsed_url = urlparse(url)
            url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            product = Product.query.filter_by(url=url)
            if product.count():
                flash("Product already in database", category='info')
                product = product.first()
                return redirect(f'/admin/product/{product.id}')

            p = Process(target=run_spider, args=(url, "url"))
            p.start()
            p.join()

            product = Product.query.filter_by(url=url)
            if product.count():
                flash("Product added to database successfully", category='success')
                product = product.first()
                return redirect(f'/admin/product/{product.id}')
            else:
                flash("Product could not be added to database", category='danger')
                flash("Check if the URL is correct and supported by our program", category='danger')
                return redirect('/admin/product/add')

        elif method == 'google':
            url = request.form.get('query')
            pages = request.form.get('pages')
            results_per_page = request.form.get('results_per_page')

            if not url:
                flash("Enter query", category='danger')
                return redirect('/admin/product/add')

            p = Process(target=run_spider, args=(url, "google", int(pages), int(results_per_page)))
            p.start()
            p.join()

            flash("Function run successfully", category='success')
            return redirect('/admin/Products/products')

    return render_template('Admin/Scraping/add.html')