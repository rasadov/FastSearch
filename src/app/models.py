from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Float
from flask_login import UserMixin
from web import db, bcrypt, app


Base = declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(), nullable=False, unique=True)
    name = Column(String(length=30), default=None)
    password_hash = Column(String(length=100), default=None)
    profile_picture = Column(String(), default='../static/images/profile/user.png')

    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def chech_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def user_exists(self) -> bool:
        """Returns True if user is registrated"""
        if User.query.filter_by(email_address=self.email_address).count():
            return True
        return False

class Product(db.Model):
    def __init__(self, url : str, title : str, price : str, item_class : str | None = None, producer : str | None = None, amount_of_ratings : str | None = None, rating : str | None = None) -> None:
        self.url = url
        self.title = title
        self.price = price
        self.item_class = item_class
        self.producer = producer
        self.amount_of_ratings = amount_of_ratings
        self.rating = rating

    id = Column(Integer(), primary_key=True)
    url = Column(String(), nullable=False)
    title = Column(String(), nullable=False)
    price = Column(String(), nullable=False)
    item_class = Column(String(), default=None)
    producer = Column(String(), default=None)
    amount_of_ratings = Column(Integer(), default=None)
    rating = Column(Float(), default=None)

# with app.app_context():
#     db.create_all()