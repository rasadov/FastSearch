"""
This file contains the routes related to the product.
~~~~~~~~~~~~~~~~~~~~~

Routes:
- GET `/`: Renders the home page.
- GET `/search`: Renders the search page with filtered products based on the query parameters.
- POST `/cart/add`: Add a product to the user's cart.
- GET `/donate`: Renders the donation page.
- GET `/contact`: Renders the contact page.
- POST `/contact`: Process the contact form submission and send an email to the admin users.


Functions:
- `home_get()`: Renders the home page.
- `search_get()`: Renders the search page with filtered products based on the query parameters.
- `add_to_cart()`: Add a product to the user's cart.
- `donation_get()`: Renders the donation page.
- `contact_get()`: Renders the contact page.
- `contact_post()`: Process the contact form submission and send an email to the admin users.
"""

from flask import jsonify
from app.models import Product, Cart, User, Message
from app import (app, render_template, login_required,
            request, redirect, current_user, DONATION_LINK,
            flash, url_for, db, login_user)
from app.__email__sender__ import send_email
from spiders.myproject.myproject.spiders.utils.converter import SignsConverter


@app.get("/")
def home_get():
    """
    Renders the home page.

    Returns:
    - Rendered template for the home page.
    """
    # if current_user.is_anonymous:
    #     login_user(User.query.get(1))
    print(current_user.is_authenticated)
    print(User.query)
    return render_template("Main/index.html")


def convert(key, val):
    """
    Convert the query parameter to the correct type.

    This function converts the query parameter to the correct type based on the key.

    Args:
    - key (str): The key of the query parameter.
    - val (str): The value of the query parameter.

    Returns:
    - The converted value of the query parameter.
    """
    if key == "min_price" or key == "max_price":
        return float(val)
    if key == "min_rating" or key == "max_rating":
        return float(val)
    return val

@app.get("/api/products")
def products_api():
    """
    Get the search results based on the query parameters.

    This function is called using AJAX to get the search results based on the query parameters.
    It retrieves the query parameters from the request and 
    filters the products based on the parameters.
    The filtered products are paginated and returned as a JSON response.

    Query Parameters:
    - search (str): The search keyword to filter products by title.
    - min_price (int): The minimum price to filter products by.
    - max_price (int): The maximum price to filter products by.
    - brand (str): The brand name to filter products by.
    - min_rating (float): The minimum rating to filter products by.
    - max_rating (float): The maximum rating to filter products by.
    - page (int): The page number to paginate the results.

    Returns:
    - JSON response with the filtered products and pagination information.
    """
    if len(request.args) < 2:
        return jsonify({"content": "message", "donation_link": DONATION_LINK})


    page = request.args.get("page", 1, type=int)

    products = Product.query

    filters = Product.get_filters(request.args)

    variables = {}
    for key, value in filters.items():
        val = request.args.get(key)
        if val not in [None, "null", ""]:
            val = convert(key, val)
            products = value[1](val, products)
            variables[key] = val

    products = products.paginate(page=page, per_page=9)

    total_pages = products.pages
    return jsonify(
        {
            "content": "products",
            "products": [
                {
                    "id": product.id,
                    "url": product.url,
                    "domain": product.get_domain(),
                    "title": product.title,
                    "price": product.price,
                    "currency": SignsConverter.convert_to_currency_sign(product.price_currency),
                    "rating": product.rating,
                    "amount_of_ratings": product.amount_of_ratings,
                    "item_class": product.item_class,
                    "producer": product.producer,
                    "image": product.get_image(),
                    "tracked": 
                    Cart.in_cart(current_user.id, product.id) if current_user.is_authenticated
                    else "Logged out",
                }
                for product in products.items
            ],
            "total_pages": total_pages,
            "current_page": page,
        }
    )

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
    return render_template(
        "Main/search.html", authenticated=current_user.is_authenticated
    )

@app.post('/cart/add')
@login_required
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
    - If the action is 'track',
    it returns a JSON response with status 'success' and action 'track'.
    - If the action is 'remove',
    it returns a JSON response with status 'success' and action 'remove'.
    - If there is an error,
    it returns a JSON response with status 'error' and HTTP status code 400.
    """

    data = request.get_json()

    if not data['product_id'] or not data['action']:
        return redirect("/")
    product = Product.query.get(data['product_id'])

    if product:
        if data['action'] == 'track':
            Cart.append(current_user.id, product.id)
            return jsonify({'status': 'success', 'action': 'track'}), 200
        Cart.remove(current_user.id, product.id)
        return jsonify({'status': 'success', 'action': 'remove'}), 200
    return jsonify({'status': 'error'}), 400


@app.get("/donate")
def donation_get():
    """
    Handler function for the GET request to '/donate' route.
    
    Returns:
        The rendered template 'Main/donate.html'.
    """
    return render_template("Main/donate.html", donation_link=DONATION_LINK)


@app.get("/contact")
def contact_get():
    """
    Handler function for the GET request to '/contact' endpoint.
    Renders the 'contact.html' template.

    Returns:
        The rendered 'contact.html' template.
    """
    return render_template("Main/contact.html")

@app.post("/contact")
def contact_post():
    """
    Process the contact form submission and send an email to the admin users.

    If the user is not logged in, they will be redirected to the login page.
    The form data is retrieved from the request and validated.
    If the name and message fields are not empty, an email is sent to all admin users.
    The email includes the sender's name, email address, phone number (if provided), and message.
    A success flash message is displayed if the message is sent successfully.
    Otherwise, an error flash message is displayed.

    Returns:
        None
    """
    if current_user.is_anonymous:
        flash("You need to be logged in to send a message", "danger")
        return redirect(url_for("login"))
    name = request.form["name"]
    number = request.form["number"]
    subject = request.form["subject"]
    message = request.form["message"]
    if name and message:
        users = User.query.filter(User.role=="admin" or User.role=="owner").all()
        for user in users:
            print(user.email_address)
            send_email(
                user.email_address,
                f"""{name} ({current_user.email_address} | {number if number else 'No number'})
                has sent you message: \n\n {message}""",
                subject=subject,
                title=f"Abyssara user sent you a message",
            )

            db.session.add(
                Message(
                    text=f"""{name}
                    ({current_user.email_address} | {number if number else 'No number'})
                    has sent you message: \n\n {message}""",
                    sender_id=current_user.id,
                    recipient_id=user.id)
                )
            db.session.commit()

        flash("Your message has been sent. Thank you!", "success")
        return redirect(url_for("home_get"))
    flash("Please fill out all the fields", "danger")
    return redirect(url_for("contact_get"))
