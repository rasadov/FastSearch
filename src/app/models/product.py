import re
from sqlalchemy import Index, Computed, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.types import TypeDecorator

from web import db, request
from .pricehistory import PriceHistory


class TSVector(TypeDecorator):
    impl = TSVECTOR


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

        __ts_vector__ (TSVector): The full-text search vector for the product.
        __table_args__ (tuple): The table arguments for the product.

    Relationships:
        price_history (list): A list of price history records associated with the product.

    Methods:
        is_available(): Checks if the product is available.
        items(): Returns a dictionary of the product's attributes.
        get_filters(): Returns a dictionary of filters for querying products.
        price_change_last(): Returns the price change of the product in the last price history entry.
        price_change_90_days(): Returns the price change of the product in the last 90 days.
        price_change_30_days(): Returns the price change of the product in the last 30 days.
        price_change_7_days(): Returns the price change of the product in the last 7 days.
        price_change_1_day(): Returns the price change of the product in the last 1 day.
    """

    # Attributes

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[str] = mapped_column(nullable=False)
    item_class: Mapped[str] = mapped_column(default=None)
    producer: Mapped[str] = mapped_column(default=None)
    amount_of_ratings: Mapped[int] = mapped_column(default=None)
    rating: Mapped[float] = mapped_column(default=None)
    availability: Mapped[bool] = mapped_column(default=None)

    tsvector_title: Mapped[TSVector] = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', title)", persisted=True),
        name="tsvector_title",
    )

    __table_args__: Mapped[Index] = (
        Index("ix_video___ts_vector__", tsvector_title, postgresql_using="gin"),
    )

    price_history: Mapped["PriceHistory"] = relationship(backref="product")

    # Methods

    def __init__(
        self,
        url,
        title,
        price,
        item_class,
        producer,
        amount_of_ratings,
        rating,
        availability,
    ):
        self.url = url
        self.title = title
        self.price = price
        self.item_class = item_class
        self.producer = producer
        self.amount_of_ratings = amount_of_ratings
        self.rating = rating
        self.availability = availability

    def is_available(self):
        """
        Checks if the product is available.

        Returns:
            bool: True if the product is available, False otherwise.
        """
        return self.availability == "In stock"

    def get_domain(self):
        """
        Returns the domain of the product's URL.

        Returns:
            str: The domain of the product's URL.
        """
        return re.search(r"(https?://)?(www\.)?([^/]+)", self.url).group(3)

    def items(self):
        """
        Returns a dictionary of the product's attributes.

        Returns:
            dict: A dictionary containing the product's attributes.
        """
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "price": self.price,
            "item_class": self.item_class,
            "producer": self.producer,
            "rating": self.rating,
            "amount_of_ratings": self.amount_of_ratings,
            "availability": self.is_available(),
        }.items()

    @staticmethod
    def search(search, query):
        """
        Perform a search operation on the given query based on the provided search string.

        This function applies filtering to the given query based on the search string. It checks if the length of the search
        string is less than 10 characters or the number of words in the search string is less than 4. If either of these
        conditions is true, it applies a filter to the query using similarity functions and the ilike operator to match
        the search string against the title, producer, and item_class attributes of the Product model.

        If the search string meets the length and word count requirements, it applies a full-text search filter to the query
        using the tsvector_title column of the Product model.

        Args:
            search (str): The search string to be used for filtering the query.
            query (Query): The query object to be filtered.

        Returns:
            Query: The filtered query object based on the search string.

        """
        if len(search) < 10 or len(search.split()) < 4:
            return query.filter((func.similarity(Product.title, search) > 0.1)
                                | (func.similarity(Product.producer, search) > 0.1)
                                | (func.similarity(Product.item_class, search) > 0.1)
                                | Product.title.ilike(f"%{search}%"))
        return query.filter(Product.tsvector_title.match(search))

    @staticmethod
    def get_filters():
        return {
            "search": [
                request.args.get("search", ""),
                Product.search],
            "min_price": [
                request.args.get("min_price", None, type=int),
                lambda min_price, query: query.filter(Product.price >= min_price),
            ],
            "max_price": [
                request.args.get("max_price", None, type=int),
                lambda max_price, query: query.filter(Product.price <= max_price),
            ],
            "brand": [
                request.args.get("brand", None),
                lambda brand, query: query.filter(
                    Product.producer.ilike(f"{brand}")
                    | Product.producer.ilike(f"%{brand}%")
                ),
            ],
            "min_rating": [
                request.args.get("min_rating", None, type=float),
                lambda rating, query: query.filter(Product.rating >= rating),
            ],
            "max_rating": [
                request.args.get("max_rating", None, type=float),
                lambda rating, query: query.filter(Product.rating <= rating),
            ],
        }

    def price_change_last(self):
        """
        Returns the price change of the product in the last price history entry.

        Returns:
            float: The price change percentage.
        """

        return PriceHistory.price_change(self.id, "last")

    def price_change_90_days(self):
        """
        Returns the price change of the product in the last 90 days.

        Returns:
            float: The price change percentage.
        """

        return PriceHistory.price_change(self.id, 90)

    def price_change_30_days(self):
        """
        Returns the price change of the product in the last 30 days.

        Returns:
            float: The price change percentage.
        """

        return PriceHistory.price_change(self.id, 30)

    def price_change_7_days(self):
        """
        Returns the price change of the product in the last 7 days.

        Returns:
            float: The price change percentage.
        """

        return PriceHistory.price_change(self.id, 7)

    def price_change_1_day(self):
        """
        Returns the price change of the product in the last 1 day.

        Returns:
            float: The price change percentage.

        """

        return PriceHistory.price_change(self.id, 1)

    def __repr__(self):
        return f"<Product {self.id}>"
