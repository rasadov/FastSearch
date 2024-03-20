from datetime import datetime, timedelta
from sqlalchemy import ForeignKey, desc 
from sqlalchemy.orm import mapped_column, Mapped

from web import db

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
        price_change(product_id, days): Returns the price change of the product in the last n days.

    """

    __tablename__ = "price_history"

    # Attributes

    price_history_id : Mapped[int] = mapped_column(primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("product.id"), nullable=False)
    price : Mapped[str] = mapped_column(nullable=False)
    change_date : Mapped[datetime] = mapped_column(nullable=False, default=datetime.now().date())

    # Methods

    def __init__(self, product_id, price, date=datetime.now().date()):
        self.product_id = product_id
        self.price = price
        self.date = date
        
    @staticmethod
    def if_price_change(product_id, days = None) -> bool:
        if not days:
            return PriceHistory.query.filter_by(product_id=product_id).count() > 1
        records = PriceHistory.query.filter_by(product_id=product_id).order_by(
            desc(PriceHistory.change_date))

        if records.count() < 2:
            return False
        
        cur = records.first().price
        
        records = records.filter(
            PriceHistory.change_date < 
            datetime.now().date() - timedelta(days=days))
        
        return records.first().price != cur.first().price

    @staticmethod
    def price_change(product_id, days = None) -> float:
        """
        Returns the price change of the product in the last n days.

        Args:
            product_id (int): The ID of the product to get the price change for.
            days (int): The number of days to get the price change for.

        Returns:
            float: The price change percentage.

        """
        
        records = PriceHistory.query.filter_by(product_id=product_id).order_by(
            desc(PriceHistory.change_date))
        
        if not days:
            cur = records.first().price
            last = records.offset(1).first().price

            cur = float(cur.replace("$", "").replace(",", ""))
            last = float(last.replace("$", "").replace(",", ""))

            return round(last / cur - 1, 2) * 100        

        if records.count() < 2:
            return 0.0
        
        cur = records.first().price
        
        records = records.filter(
            PriceHistory.change_date < 
            datetime.now().date() - timedelta(days=days))
        
        if not records.count():
            return 0.0
        else:
            records = records.order_by(desc(PriceHistory.change_date))

        last = records.first()

        cur = float(cur.replace("$", "").replace(",", ""))
        last = float(last.replace("$", "").replace(",", ""))

        return round(last / cur - 1, 2) * 100
