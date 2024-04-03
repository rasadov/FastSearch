"""
This module contains functions for interacting with the database.

The functions in this module are used to save products to the database or update existing products if they already exist.
"""

import os
import psycopg2

from app.__notifications__ import notify_price_change


DB_USER = os.environ.get("DB_USER")
DB_NAME = os.environ.get("DB_NAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

def save_product_to_database(
    url: str,
    title: str,
    price: float,
    price_currency: str,
    rating: float =None,
    amount_of_ratings: int =None,
    item_class: str=None,
    producer: str=None,
    image_url: str=None,
    availability: str='In stock'
):
    """
    Saves a product to the database or updates an existing product if it already exists.

    Parameters:
    - url (str): The URL of the product.
    - title (str): The title of the product.
    - price (float): The price of the product.
    - price_currency (str): The currency of the price.
    - rating (float, optional): The rating of the product. Defaults to None.
    - amount_of_ratings (int, optional): The number of ratings for the product. Defaults to None.
    - item_class (str, optional): The class/category of the product. Defaults to None.
    - producer (str, optional): The producer/manufacturer of the product. Defaults to None.

    If the product already exists in the database, the function checks for changes in price, rating, and amount of ratings.
    If the price has changed, it updates the data in the `product` table and saves the price change in the `price_history` table.
    If the rating has changed, it updates the record in the `product` table.
    If the product does not exist in the database, it adds a new record to the `product` table and starts tracking the price in the `price_history` table.
    """

    conn = psycopg2.connect(
        database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    curr = conn.cursor()

    curr.execute(f"""SELECT * FROM product WHERE url = '{url}';""")

    result = curr.fetchone()

    curr.execute(
        """
                    CREATE TABLE IF NOT EXISTS price_history (
                    price_history_id SERIAL PRIMARY KEY,
                    product_id INT,
                    price INT NOT NULL,
                    price_currency VARCHAR(255) NOT NULL,
                    change_date DATE NOT NULL,

                    FOREIGN KEY (product_id) REFERENCES product(id)
                    );"""
    )

    # Checking if this record already exists in database
    if result:
        price_in_db = result[3]
        amount_of_rating_in_db = result[6]
        rating_in_db = result[7]

        if (
            price_in_db != price
            or rating_in_db != rating
            or amount_of_rating_in_db != amount_of_ratings
        ):

            # Checking if price of product has changed
            if price_in_db != price:

                if price_in_db > price:
                    notify_price_change(url)

                product_id = result[0]

                # Saving price change to keep track of price
                curr.execute(
                    """
                    INSERT INTO price_history (product_id, price, price_currency, change_date)
                    VALUES (%s, %s, %s, CURRENT_DATE);
                """,
                    (product_id, price, price_currency),
                )

            curr.execute(
                f"""
                UPDATE product
                SET price = %s, price_currency=%s, title = %s, item_class = %s, producer = %s,
                    amount_of_ratings = %s, rating = %s, image_url = %s, availability = %s
                WHERE url = %s;
            """,
                (price, price_currency, title, item_class, producer, amount_of_ratings, rating, image_url,availability, url),
            )
    else:
        # This product does not exist, insert a new record into the database
        try:
            curr.execute(
                """
                INSERT INTO product (url, title, price, price_currency, item_class,
                producer, amount_of_ratings, rating, image_url, availability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (url, title, price, price_currency, item_class, producer, amount_of_ratings, rating, image_url, availability),
            )
        except Exception as e:
            print(f"An error occurred: {e}")
        

        curr.execute(f"""SELECT * FROM product WHERE url = '{url}';""")

        result = curr.fetchone()

        product_id = result[0]

        curr.execute(
            """
            INSERT INTO price_history (product_id, price, price_currency, change_date)
            VALUES (%s, %s, %s, CURRENT_DATE);
        """,
            (product_id, price, price_currency),
        )


    conn.commit()
    curr.close()
    conn.close()
