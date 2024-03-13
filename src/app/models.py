from sqlalchemy import Integer, String, Column, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from web import db, bcrypt, app
from datetime import datetime


Base = declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    def __init__(self, email_address, password = None,username=None, name=None, confirmed_on=None, subscribed_till=None, role='user'):
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
        return self.role == 'admin' or self.role == 'owner'
    
    def is_owner(self):
        return self.role == 'owner'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        if plain_text_password is None:
            return
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def chech_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def username_exists(username):
        return User.query.filter_by(username=username).count()
    
    def user_exists(email_address) -> bool:
        """Returns True if user is registrated"""
        return User.query.filter_by(email_address=email_address).count()
    
    def is_confirmed(self):
        return self.confirmed_on != None

    def is_subscribed(self):
        if self.role == 'admin' or self.role == 'owner':
            return True
        return self.subscribed_till and self.subscribed_till > datetime.now()
    
    def items(self):
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
        return f'<User {self.id}>'

class Product(db.Model):
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


    def is_avialable(self):
        return self.availability == "In stock"
    
    def items(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'price': self.price,
            'item_class': self.item_class,
            'producer': self.producer,
            'rating': self.rating,
            'amount_of_ratings': self.amount_of_ratings,
            'availability': self.is_avialable()
        }.items()

    def __repr__(self):
        return f'<Product {self.id}>'
    

class PriceHistory(db.Model):
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