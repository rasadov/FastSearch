"""
This module contains the Product model for the application.
"""

import re
from sqlalchemy import Index, Computed, func
from flask_sqlalchemy.query import Query
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app import db
from app.models.pricehistory import PriceHistory
from app.models.ts_vector import TSVector


class Product(db.Model):
    """
    Represents a product in the application.

    Attributes:
        url (str): The URL of the product.
        title (str): The title of the product.
        price (float): The price of the product.
        price_currency (str): The currency of the price.
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
        get_domain(): Returns the domain of the product's URL.
        items(): Returns a dictionary of the product's attributes.
        get_attributes(): Returns a dictionary of the product's attributes for editing.
        get_image(): Returns the image URL of the product.
        search(search, query): Performs a search operation on the given
        query based on the provided search string.
        get_filters(): Returns a dictionary of filters for querying products.
        price_change(days=None): Returns the price change of the product
        in the last price history entry.
    """

    # Attributes

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    price_currency: Mapped[str] = mapped_column(default="USD", nullable=False)
    item_class: Mapped[str] = mapped_column(default=None, nullable=True)
    producer: Mapped[str] = mapped_column(default=None, nullable=True)
    amount_of_ratings: Mapped[int] = mapped_column(default=None, nullable=True)
    rating: Mapped[float] = mapped_column(default=None, nullable=True)
    image_url: Mapped[str] = mapped_column(default=None, nullable=True)
    availability: Mapped[str] = mapped_column(default=None, nullable=True)

    tsvector_title: Mapped[TSVector] = mapped_column(
        TSVector(),
        Computed("to_tsvector('english', title)", persisted=True),
        name="tsvector_title",
    )

    __table_args__ = (
        Index("ix_product_tsvector_title", tsvector_title, postgresql_using="gin"),
        {"extend_existing": True},
    )

    price_history: Mapped["PriceHistory"] = relationship(backref="product")

    # Methods

    def is_available(self) -> bool:
        """
        Checks if the product is available.

        Returns:
            bool: True if the product is available, False otherwise.
        """
        return self.availability == "In stock"

    def get_domain(self) -> str:
        """
        Returns the domain of the product's URL.

        Returns:
            str: The domain of the product's URL.
        """
        return re.search(r"(https?://)?(www\.)?([^/]+)", self.url).group(3)

    def to_dict(self) -> dict:
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
        }

    def get_attributes(self) -> dict:
        """
        Returns a dictionary of the product's attributes for editing.

        Returns:
            dict: A dictionary containing the product's attributes for editing.
        """
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "price": self.price,
            "price_currency": self.price_currency,
            "item_class": self.item_class,
            "producer": self.producer,
            "rating": self.rating,
            "amount_of_ratings": self.amount_of_ratings,
            "availability": self.availability,
            "image_url": self.image_url,
        }

    def get_image(self) -> str:
        """
        Returns the image URL of the product.

        Returns:
            str: The image URL of the product.
        """
        return self.image_url

    @staticmethod
    def search(search: str, query: Query) -> Query:
        """
        Perform a search operation on the given query based on the provided search string.

        This function applies filtering to the given query based on the search string.
        It checks if the length of the search
        string is less than 10 characters or the number of words
        in the search string is less than 4. If either of these
        conditions is true, it applies a filter to the query using
        similarity functions and the ilike operator to match
        the search string against the title, producer,
        and item_class attributes of the Product model.

        If the search string meets the length and word count requirements,
        it applies a full-text search filter to the query
        using the tsvector_title column of the Product model.

        Args:
            search (str): The search string to be used for filtering the query.
            query (Query): The query object to be filtered.

        Returns:
            Query: The filtered query object based on the search string.

        """
        try:
            if len(search) < 10 or len(search.split()) < 3:
                return query.filter((func.similarity(Product.title, search) > 0.1)
                                    | (func.similarity(Product.producer, search) > 0.1)
                                    | (func.similarity(Product.item_class, search) > 0.1)
                                    | Product.title.ilike(f"%{search}%")).order_by(
                    func.similarity(Product.title, search).desc()
                )
            return query.filter(Product.tsvector_title.match(search))
        except Exception as e:
            raise func.__dir__()
    @staticmethod
    def get_filters(src: dict) -> dict:
        """
        Returns a dictionary of filters based on the source.

        The dictionary contains filter names as keys and a list as values.
        Each list contains two elements:
        - The first element is the value obtained from the source.
        - The second element is a lambda function that takes the filter value
          and a query object as arguments, and applies the filter to the query.

        Available filters:
        - "search": Filters products based on a search term.
        - "min_price": Filters products based on a minimum price.
        - "max_price": Filters products based on a maximum price.
        - "brand": Filters products based on a brand name.
        - "min_rating": Filters products based on a minimum rating.
        - "max_rating": Filters products based on a maximum rating.

        Returns:
        A dictionary of filters.
        """
        return {
            "search": [
                src.get("search", ""),
                Product.search
            ],
            "min_price": [
                src.get("min_price", None, type=int),
                lambda min_price, query: query.filter(Product.price >= min_price),
            ],
            "max_price": [
                src.get("max_price", None, type=int),
                lambda max_price, query: query.filter(Product.price <= max_price),
            ],
            "brand": [
                src.get("brand", None),
                lambda brand, query: query.filter(
                    Product.producer.ilike(f"{brand}")
                    | Product.producer.ilike(f"%{brand}%")
                ),
            ],
            "min_rating": [
                src.get("min_rating", None, type=float),
                lambda rating, query: query.filter(Product.rating >= rating),
            ],
            "max_rating": [
                src.get("max_rating", None, type=float),
                lambda rating, query: query.filter(Product.rating <= rating),
            ],
        }

    def price_change(self, days=None) -> float:
        """
        Returns the price change of the product in the last price history entry.

        Args:
            days (int, optional): The number of days to check for price change. Defaults to None.

        Returns:
            float: The price change percentage.

        """
        if PriceHistory.if_price_change(self.id):
            if days:
                return PriceHistory.price_change(self.id, days)
            return PriceHistory.price_change(self.id)
        return 0.0

    def __repr__(self) -> str:
        """
        Returns a string representation of the product.

        Returns:
            str: The string representation of the product.
        """
        return f"<Product {self.id}>"
