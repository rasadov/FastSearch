from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Float
from flask_login import UserMixin
from web import db, bcrypt, app
from datetime import datetime


Base = declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(length=30), unique=True, default=None)
    name = Column(String(length=30), default=None)
    email_address = Column(String(), nullable=False, unique=True)
    password_hash = Column(String(length=100), default=None)

    # Commented code below is not finished
    # created_on = db.Column(db.DateTime, nullable=False)
    # is_admin = db.Column(db.Boolean, nullable=False, default=False)
    # is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    # confirmed_on = db.Column(db.DateTime, nullable=True)

    # def __init__(
    #     self, email, password, is_admin=False, is_confirmed=False, confirmed_on=None
    # ):
    #     self.email = email
    #     self.password = bcrypt.generate_password_hash(password)
    #     self.created_on = datetime.now()
    #     self.is_admin = is_admin
    #     self.is_confirmed = is_confirmed
    #     self.confirmed_on = confirmed_on
    
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
    
    def __repr__(self):
        return f'<User {self.id}>'

class Product(db.Model):
    id = Column(Integer(), primary_key=True)
    url = Column(String(), nullable=False)
    title = Column(String(), nullable=False)
    price = Column(String(), nullable=False)
    item_class = Column(String(), default=None)
    producer = Column(String(), default=None)
    amount_of_ratings = Column(Integer(), default=None)
    rating = Column(Float(), default=None)

    def __repr__(self):
        return f'<Product {self.id}>'

with app.app_context():
    db.create_all()