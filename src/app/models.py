"""
This module contains the models for the application.
~~~~~~~~~~~~~~~~~~~~~

The models in this module represent the entities in the application, such as users and products.
Each model class defines the attributes and methods associated with the entity it represents.

Classes:
- User: Represents a user in the application.
- Product: Represents a product in the application.
- PriceHistory: Represents the price history of a product.

The User class represents a user in the application. It contains attributes such as username, email address, and password.
The class also provides methods for checking user privileges, managing passwords, and checking user existence.

The Product class represents a product in the application. It contains attributes such as URL, title, and price.
The class provides methods for checking product availability and retrieving product attributes.

The PriceHistory class represents the price history of a product. It is associated with a specific product and contains information about the price changes over time.

Note: This module uses SQLAlchemy for database operations and Flask-Login for user authentication.

"""

from sqlalchemy import Integer, String, Column, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from web import db, bcrypt, app, s, SignatureExpired
from datetime import datetime


Base = declarative_base()

class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        name (str): The name of the user.
        email_address (str): The email address of the user.
        password_hash (str): The hashed password of the user.
        created_on (datetime): The date and time when the user was created.
        role (str): The role of the user.
        confirmed_on (datetime): The date and time when the user was confirmed.
        subscribed_till (datetime): The date and time until which the user is subscribed.

    Methods:
        is_admin(): Checks if the user has admin privileges.
        is_owner(): Checks if the user is the owner.
        password(): Gets the password of the user.
        password.setter(): Sets the password of the user.
        chech_password_correction(attempted_password): Checks if the attempted password is correct.
        username_exists(username): Checks if a user with the given username exists.
        user_exists(email_address): Checks if a user with the given email address exists.
        is_confirmed(): Checks if the user is confirmed.
        is_subscribed(): Checks if the user is subscribed.
        items(): Returns a dictionary of the user's attributes.
        get_reset_token(expires_sec): Generates a reset token for the user.
        verify_reset_token(token): Verifies a reset token for the user.
        __repr__(): Returns a string representation of the user.

    """

    __tablename__ = 'user'

    def __init__(self, email_address, password=None, username=None, name=None, confirmed_on=None, subscribed_till=None, role='user'):
        """
        Initializes a new instance of the User class.

        Args:
            email_address (str): The email address of the user.
            password (str, optional): The password of the user. Defaults to None.
            username (str, optional): The username of the user. Defaults to None.
            name (str, optional): The name of the user. Defaults to None.
            confirmed_on (datetime, optional): The date and time when the user was confirmed. Defaults to None.
            subscribed_till (datetime, optional): The date and time until which the user is subscribed. Defaults to None.
            role (str, optional): The role of the user. Defaults to 'user'.
        """
        self.username = username
        self.email_address = email_address
        self.password = password
        self.name = name
        self.confirmed_on = confirmed_on
        self.subscribed_till = subscribed_till
        self.role = role

    id = Column(Integer, primary_key=True)
    username = Column(String(length=30), unique=True, default=None)
    name = Column(String(length=30), default=None)
    email_address = Column(String(), nullable=False, unique=True)
    password_hash = Column(String(length=100), default=None)

    created_on = Column(DateTime, nullable=False, default=str(datetime.now())[:19])
    role = Column(String, nullable=False, default='user')
    confirmed_on = Column(DateTime, nullable=True)

    subscribed_till = Column(DateTime, nullable=True, default=None)
    
    def is_admin(self):
        """
        Checks if the user has admin privileges.

        Returns:
            bool: True if the user has admin privileges, False otherwise.
        """
        return self.role == 'admin' or self.role == 'owner'
    
    def is_owner(self):
        """
        Checks if the user is the owner.

        Returns:
            bool: True if the user is the owner, False otherwise.
        """
        return self.role == 'owner'

    @property
    def password(self):
        """
        Gets the password of the user.

        Returns:
            str: The password of the user.
        """
        return self.password

    @password.setter
    def password(self, plain_text_password):
        """
        Sets the password of the user.

        Args:
            plain_text_password (str): The plain text password to set.
        """
        if plain_text_password is None:
            return
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def chech_password_correction(self, attempted_password):
        """
        Checks if the attempted password is correct.

        Args:
            attempted_password (str): The password to check.

        Returns:
            bool: True if the attempted password is correct, False otherwise.
        """
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def username_exists(username):
        """
        Checks if a user with the given username exists.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if a user with the given username exists, False otherwise.
        """
        return User.query.filter_by(username=username).count()
    
    def user_exists(email_address) -> bool:
        """
        Checks if a user with the given email address exists.

        Args:
            email_address (str): The email address to check.

        Returns:
            bool: True if a user with the given email address exists, False otherwise.
        """
        return User.query.filter_by(email_address=email_address).count()
    
    def is_confirmed(self):
        """
        Checks if the user is confirmed.

        Returns:
            bool: True if the user is confirmed, False otherwise.
        """
        return self.confirmed_on != None

    def is_subscribed(self):
        """
        Checks if the user is subscribed.

        Returns:
            bool: True if the user is subscribed, False otherwise.
        """
        if self.role == 'admin' or self.role == 'owner':
            return True
        return self.subscribed_till and self.subscribed_till > datetime.now()
    
    def get_reset_token(self):
            """
            Generates a reset token for the user.

            Returns:
                str: The reset token.
            """
            return s.dumps({'user_id': self.id}, salt='password-reset')

    @staticmethod
    def verify_reset_token(token):
        """
        Verify the validity of a password reset token.

        Parameters:
        - token (str): The password reset token to be verified.

        Returns:
        - User or None: The User object associated with the token if it is valid, otherwise None.
        """
        try:
            user_id = s.loads(token, salt='password-reset', max_age=1800)['user_id']
        except SignatureExpired:
            return None
        return User.query.get(user_id)

    def items(self):
        """
        Returns a dictionary of the user's attributes.

        Returns:
            dict: A dictionary of the user's attributes.
        """
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'email_address': self.email_address,
            'role': self.role,
            'confirmed_on': self.confirmed_on,
            'subscribed_till': self.subscribed_till
        }.items()

    def __repr__(self):
        """
        Returns a string representation of the user.

        Returns:
            str: A string representation of the user.
        """
        return f'<User {self.id}>'

class Product(db.Model):
    """
    Represents a product in the application.

    Attributes:
        url (str): The URL of the product.
        title (str): The title of the product.
        price (str): The price of the product.
        item_class (str, optional): The class of the product.
        producer (str, optional): The producer of the product.
        amount_of_ratings (int, optional): The number of ratings for the product.
        rating (float, optional): The rating of the product.
        availability (bool, optional): The availability of the product.

    Relationships:
        price_history (list): A list of price history records associated with the product.

    Methods:
        is_available(): Checks if the product is available.
        items(): Returns a dictionary of the product's attributes.
    """

    def __init__(self, url, title, price, item_class, producer, amount_of_ratings, rating, availability):
        self.url = url
        self.title = title
        self.price = price
        self.item_class = item_class
        self.producer = producer
        self.amount_of_ratings = amount_of_ratings
        self.rating = rating
        self.availability = availability
    
    id = Column(Integer(), primary_key=True)
    url = Column(String(), nullable=False)
    title = Column(String(), nullable=False)
    price = Column(String(), nullable=False)
    item_class = Column(String(), default=None)
    producer = Column(String(), default=None)
    amount_of_ratings = Column(Integer(), default=None)
    rating = Column(Float(), default=None)
    availability = Column(Boolean(), default=None)

    price_history = relationship("PriceHistory", backref="product")


    def is_available(self):
        """
        Checks if the product is available.

        Returns:
            bool: True if the product is available, False otherwise.
        """
        return self.availability == "In stock"
    
    def items(self):
        """
        Returns a dictionary of the product's attributes.

        Returns:
            dict: A dictionary containing the product's attributes.
        """
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'price': self.price,
            'item_class': self.item_class,
            'producer': self.producer,
            'rating': self.rating,
            'amount_of_ratings': self.amount_of_ratings,
            'availability': self.is_available()
        }.items()

    def __repr__(self):
        return f'<Product {self.id}>'
    

class PriceHistory(db.Model):
    """
    Represents the price history of a product.

    Attributes:
        price_history_id (int): The unique identifier for the price history entry.
        product_id (int): The ID of the product associated with the price history.
        price (str): The price of the product at a specific date.
        change_date (datetime): The date and time when the price was changed.

    Methods:
        __init__(product_id, price, date): Initializes a new instance of the PriceHistory class.

    """
    __tablename__ = 'price_history'
    def __init__(self, product_id, price, date):
        self.product_id = product_id
        self.price = price
        self.date = date

    price_history_id = Column(Integer(), primary_key=True)
    product_id = Column(Integer(), ForeignKey('product.id'), nullable=False)
    price = Column(String(), nullable=False)
    change_date = Column(DateTime(), nullable=False, default=str(datetime.now())[:19])

with app.app_context():
    db.create_all()