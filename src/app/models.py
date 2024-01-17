from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column
from flask_login import UserMixin
from web import db, bcrypt


Base = declarative_base()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(), nullable=False, unique=True)
    name = Column(String(length=30), default=None)
    password_hash = Column(String(length=100), default=None)
    profile_picture = Column(String())

    
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
    id = db.Column(db.Integer(), primary_key=True)
