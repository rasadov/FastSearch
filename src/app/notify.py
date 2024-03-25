from models import Product, Cart, User
from email_sender import send_email

def notify_price_change(url):
    products = Product.query.filter_by(url=url).first()

    users = [User.query.get(i.user_id) for i in  Cart.query.filter_by(product_id=products.id).all()]
    for i in users:
        send_email(
            i.email_address,
            f"The price of '{products.title}' has changed. The new price is {products.price}.",
            "Price Change Notification from Abyssara",
            "Price dropped"
        )
