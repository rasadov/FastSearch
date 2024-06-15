"""
This module contains the Cart model which represents a cart in the application.
"""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.config import db
from .user import User
from .product import Product

class Cart(db.Model):
    """
    Represents a cart in the application.

    Attributes:
        id (int): The unique identifier for the cart.
        user_id (int): The ID of the user associated with the cart.
        product_id (int): The ID of the product in the cart.
        user (User): The user associated with the cart.
        product (Product): The product in the cart.

    Methods:
        __init__(user_id, product_id): Initializes a new instance of the Cart class.
        items(user_id): Retrieves all the items in the cart for the specified user.
        add_to_cart(user_id, product_id): Adds a new item to the cart for the specified user.
        remove_from_cart(user_id, product_id): Removes an item from the cart for the specified user.
    """

    __tablename__ = "cart"
    __table_args__ = {'extend_existing': True}

    id : Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id = mapped_column(Integer(), ForeignKey("UserModel.id"), nullable=False)
    product_id = mapped_column(Integer(), ForeignKey("product.id"), nullable=False)
    user: Mapped["User"] = relationship(backref="cart")
    product: Mapped["Product"] = relationship(backref="cart")

    def __init__(self, user_id, product_id) -> None:
        """
        Initializes a new instance of the Cart class.

        Args:
            user_id (int): The ID of the user associated with the cart.
            product_id (int): The ID of the product in the cart.
        """
        self.user_id = user_id
        self.product_id = product_id

    @staticmethod
    def items(user_id) -> list:
        """
        Retrieves all the items in the cart for the specified user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of Cart objects representing the items in the cart.
        """
        return [i.product for i in Cart.query.filter_by(user_id=user_id).all()]

    @staticmethod
    def append(user_id, product_id) -> None:
        """
        Adds a new item to the cart for the specified user.

        Args:
            user_id (int): The ID of the user.
            product_id (int): The ID of the product to add to the cart.
        """
        if Cart.in_cart(user_id, product_id):
            return
        cart = Cart(user_id, product_id)
        db.session.add(cart)
        db.session.commit()

    @staticmethod
    def in_cart(user_id, product_id) -> bool:
        """
        Checks if a product is in the cart for the specified user.

        Args:
            user_id (int): The ID of the user.
            product_id (int): The ID of the product to check in the cart.

        Returns:
            bool: True if the product is in the cart, False otherwise.
        """
        return Cart.query.filter_by(user_id=user_id, product_id=product_id).first() is not None

    @staticmethod
    def remove(user_id, product_id) -> None:
        """
        Removes an item from the cart for the specified user.

        Args:
            user_id (int): The ID of the user.
            product_id (int): The ID of the product to remove from the cart.
        """
        cart = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
        db.session.delete(cart)
        db.session.commit()

    @staticmethod
    def clear(user_id) -> None:
        """
        Clears the cart for the specified user.

        Args:
            user_id (int): The ID of the user.
        """
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
