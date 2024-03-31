"""
This module contains functions for sending notifications
to users about price changes for specific products.

Functions:
- notify_price_change: Notifies users about a price change for a specific product.
"""

from app.models import Product, Cart, User
from app.__email__sender__ import send_email

def notify_price_change(url):
    """
    Notifies users about a price change for a specific product.

    Args:
        url (str): The URL of the product.

    Returns:
        None
    """
    products = Product.query.filter_by(url=url).first()

    users = [User.query.get(i.user_id) for i in  Cart.query.filter_by(product_id=products.id).all()]
    for i in users:
        send_email(
            i.email_address,
            f"The price of '{products.title}' has changed. The new price is {products.price}.",
            "Price Change Notification From Abyssara",
            "Price dropped"
        )
