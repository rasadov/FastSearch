from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, Float, DateTime, Boolean
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

    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    role = Column(String, nullable=False, default='user')
    is_confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)
    
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def chech_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    def check_username(username):
        return User.query.filter_by(username=username).count()
    
    def user_exists(email_address) -> bool:
        """Returns True if user is registrated"""
        return User.query.filter_by(email_address=email_address).count()
        
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