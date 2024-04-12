from flask import jsonify, request

from app import app
from app.models import Product, Cart
from spiders.myproject.myproject.spiders.utils.converter import SignsConverter
from flask_login import current_user

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
    if key in ("min_price","max_price"):
        return float(val)
    if key in ("min_rating","max_rating"):
        return float(val)
    return val

@app.get("/api/search")
def search_api() -> jsonify:
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

    products = products.paginate(page=page, per_page=18)

    total_pages = products.pages
    return jsonify(
        {
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
