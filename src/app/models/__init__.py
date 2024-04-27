"""
This module contains the models for the application.
~~~~~~~~~~~~~~~~~~~~~

The models in this module represent the entities in the application, such as users and products.
Each model class defines the attributes and methods associated with the entity it represents.

Classes:
-------
- User: Represents a user in the application.
- Product: Represents a product in the application.
- PriceHistory: Represents the price history of a product.
- Cart: Represents a cart in the application.
- Message: Represents a message in the application.

The User class represents a user in the application. 
It contains attributes such as username, email address, and password.
The class also provides methods for checking user privileges,
managing passwords, and checking user existence.

The Product class represents a product in the application.
It contains attributes such as URL, title, and price.
The class provides methods for checking
product availability and retrieving product attributes.

The PriceHistory class represents the price history of a product. 
It is associated with a specific product and
contains information about the price changes over time.

The Cart class represents a cart in the application.
It contains attributes such as user ID and product ID.
The class provides methods for managing items in the cart,
such as adding and removing items.

The Message class represents a message in the application.
It contains attributes such as sender ID, recipient ID, and content.
The class provides methods for sending and receiving messages.

Note: This module uses SQLAlchemy for database operations
and Flask-Login for user authentication.
"""

from sqlalchemy.ext.declarative import declarative_base

from app.models.user import User
from app.models.product import Product
from app.models.pricehistory import PriceHistory
from app.models.cart import Cart
from app.models.message import Message

Base = declarative_base()

__all__ = ["User", "Product", "PriceHistory", "Cart", "Message"]