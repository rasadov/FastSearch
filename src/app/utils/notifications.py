"""
This module contains functions for sending notifications
to users about price changes for specific products.

Functions:
- notify_price_change: Notifies users about a price change for a specific product.
"""

from app.models import Product, Cart, User
from app.utils.email import send_email

def notify_price_change(url) -> None:
    """
    Notifies users about a price change for a specific product.

    Args:
        url (str): The URL of the product.

    Returns:
        None
    """
    product: Product = Product.query.filter_by(url=url).first()

    users: list[User] = [User.query.get(i.user_id) for i in Cart.query.filter_by(product_id=product.id).all()]
    for user in users:
        if user.is_confirmed():
            send_email(
                user.email_address,
                f"The price of '{product.title}' has changed. The new price is {product.price}.",
                "Price Change Notification From Abyssara",
                "Price dropped"
            )
