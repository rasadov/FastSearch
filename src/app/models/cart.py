from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship, mapped_column, Mapped

from web import db
from .user import User
from .product import Product

class Cart(db.Model):
    __tablename__ = "cart"

    id : Mapped[int] = mapped_column(Integer(), primary_key=True)
    user_id = mapped_column(Integer(), ForeignKey("user.id"), nullable=False)    
    product_id = mapped_column(Integer(), ForeignKey("product.id"), nullable=False)
    
    user: Mapped["User"] = relationship(backref="cart")
    product: Mapped["Product"] = relationship(backref="cart")