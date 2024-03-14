"""
This module contains functions for searching, parsing, and saving data to the database.

Functions:
    - search functions for spider: search, google_custom_search
    - database functions for storing scraped data: save_product_to_database
    - parsing functions for spider: scrape_ebay_item, scrape_amazon_uk_item, scrape_newegg_item, scrape_gamestop_item, parsing_method

Dependencies:
    - psycopg2: Python-PostgreSQL Database Adapter
    - dotenv: Loads environment variables from a .env file
    - os: Provides a way to access environment variables
    - re: Regular expression operations
    - requests: HTTP library for making requests
    - json: JSON encoder and decoder
    - urllib.parse: URL handling module
    - flask: Micro web framework for building web applications

Environment Variables:
    - GOOGLE_SEARCH_ENGINE_API: API key for Google Custom Search Engine
    - GOOGLE_CX: Custom search engine ID
    - DB_USER: Database username
    - DB_NAME: Database name
    - DB_PASSWORD: Database password
    - DB_HOST: Database host
    - DB_PORT: Database port

Note: This module is part of a web scraping project and is intended to be used in a specific context.

Usage:
    - Import the module: `import utils`
    - Call the desired functions from the module: `utils.search(query, method, total_pages)`

For more details on each function, refer to their respective docstrings.
"""

import psycopg2
import dotenv
import os
import re
import requests
import json
from urllib.parse import urlparse
from flask import flash

dotenv.load_dotenv()

GOOGLE_SEARCH_API = os.environ.get("GOOGLE_SEARCH_ENGINE_API") 
GOOGLE_CX = os.environ.get("GOOGLE_CX")

DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')


################### Search functions

import requests

def google_custom_search(query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX):
    """
    Searches Google using the Custom Search API.

    Args:
        query (str): The search query.
        start_index (int): The index of the first search result to retrieve.

    Returns:
        dict: The search results in JSON format.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    Example:
        >>> results = google_custom_search('GitHub Copilot', 1)
        >>> print(results['items'][0]['title'])
        'GitHub Copilot - AI Pair Programmer'
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_SEARCH_API,
        'cx': GOOGLE_CX,
        'q': query,
        'start': start_index,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results
    except requests.exceptions.RequestException as e:
        return None

def search(query: str, method: str, total_pages: int | None = None):
    """
    Returns links for the given query and method.

    Parameters:
        query (str): The URL or query you want to search for.
        method (str): The website you are going to use for searching.
        total_pages (int, optional): The number of pages to retrieve links from. 
            If it is a one-page website, there is no need to set this parameter.

    Yields:
        str: The link for each page found.

    Raises:
        ValueError: If an invalid method is provided.

    Example:
        >>> for link in search('python', 'google', total_pages=3):
        ...     print(link)
        https://www.google.com/search?q=python
        https://www.google.com/search?q=python&page=2
        https://www.google.com/search?q=python&page=3
    """
    if method == 'google':
        for page in range(1, total_pages + 1):
            start_index = (page - 1) * 10
            results = google_custom_search(query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX)
            if results:
                for item in results.get('items', []):
                    link = item.get('link')
                    yield link

    elif method == 'url':
        yield query

    else:
        raise ValueError(f"Invalid method: {method}")

################### Database functions

def save_product_to_database(url, title, price, rating=None, amount_of_ratings=None, item_class=None, producer=None):
    """
    Saves a product to the database or updates an existing product if it already exists.

    Parameters:
    - url (str): The URL of the product.
    - title (str): The title of the product.
    - price (str): The price of the product.
    - rating (float, optional): The rating of the product. Defaults to None.
    - amount_of_ratings (int, optional): The number of ratings for the product. Defaults to None.
    - item_class (str, optional): The class/category of the product. Defaults to None.
    - producer (str, optional): The producer/manufacturer of the product. Defaults to None.

    If the product already exists in the database, the function checks for changes in price, rating, and amount of ratings.
    If the price has changed, it updates the data in the `product` table and saves the price change in the `price_history` table.
    If the rating has changed, it updates the record in the `product` table.
    If the product does not exist in the database, it adds a new record to the `product` table and starts tracking the price in the `price_history` table.
    """
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    curr = conn.cursor()
 
    curr.execute(f"""SELECT * FROM product WHERE url = '{url}';""") 

    result = curr.fetchone()

    curr.execute("""
                    CREATE TABLE IF NOT EXISTS price_history (
                    price_history_id SERIAL PRIMARY KEY,
                    product_id INT,
                    price VARCHAR(255),
                    change_date DATE NOT NULL,

                    FOREIGN KEY (product_id) REFERENCES product(id)
                    );""")

    # Checking if this record already exists in database
    if result:
        price_in_db = result[3]  
        amount_of_rating_in_db = result[6]
        rating_in_db = result[7]

        if price_in_db != price or rating_in_db != rating or amount_of_rating_in_db != amount_of_ratings:

            # Checking if price of product has changed
            if price_in_db != price:
                product_id = result[0]

                # Saving price change to keep track of price
                curr.execute("""
                    INSERT INTO price_history (product_id, price, change_date)
                    VALUES (%s, %s, CURRENT_DATE);
                """, (product_id, price))


            curr.execute(f"""
                UPDATE product
                SET price = %s, title = %s, item_class = %s, producer = %s,
                    amount_of_ratings = %s, rating = %s
                WHERE url = %s;
            """, (price, title, item_class, producer, amount_of_ratings, rating, url))
    else:
        # This product does not exist, insert a new record into the database
        curr.execute("""
            INSERT INTO product (url, title, price, item_class, producer, amount_of_ratings, rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (url, title, price, item_class, producer, amount_of_ratings, rating))
        

        curr.execute(f"""SELECT * FROM product WHERE url = '{url}';""") 
        
        result = curr.fetchone()

        product_id = result[0]
        
        curr.execute("""
            INSERT INTO price_history (product_id, price, change_date)
            VALUES (%s, %s, CURRENT_DATE);
        """, (product_id, price))
        
    conn.commit()
    curr.close()
    conn.close()

################### Web Scraping functions
"""
Note: All functions that start with `scrape` are parsing functions for different websites.
"""
    
def scrape_amazon_item(response, url: None | str = None):
    """
    Extracts data from the item page in amazon.com

    Args:
        response (obj): The response object from the web scraping request.
        url (str, optional): The URL of the item page. Defaults to None.

    Returns:
        None

    Raises:
        None

    Example:
        >>> scrape_amazon_item(response, 'https://www.amazon.com/product')
    """
    try:
        title = response.css('#productTitle::text').get().strip()
        price = f'{response.css("span.a-price-whole::text").get()}.{response.css("span.a-price-fraction::text").get()} {response.css("span.a-price-symbol::text").get()}'.strip()
        try:
            rating = float(re.findall(r'\d+\.\d+', response.css("span.a-icon-alt::text").get())[0])
            amount_of_ratings = int(response.css("a#acrCustomerReviewLink span#acrCustomerReviewText::text").get().strip().replace(',', '').split(' ')[0])
        except Exception:
            rating = None
            amount_of_ratings = 0
        try:
            producer = response.css('tr.po-brand span.po-break-word::text').get().strip()
        except Exception:
            producer = None
        try:
            item_class = response.css("div#wayfinding-breadcrumbs_feature_div ul li")[-1].css("a::text").get().strip()
        except Exception:
            item_class = None

        save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)
    
    except Exception as e:
        flash(f"Error: {e}", "danger")
    

def scrape_ebay_item(response, url: str, method : str = "add"):
    """
    Extracts data from the item page on `ebay.com`
    Not finished
    """
    title = response.css('title::text').get()
    price = response.css('div.x-price-primary span.ux-textspans::text').get()
        

def scrape_amazon_uk_item(response, url: None | str = None):
    """
    Extracts data from item page in amazon.co.uk
    Not finished
    """
    title = response.css('#productTitle::text').get().strip()
    price = f'{response.css("span.a-price-whole::text").get()}.{response.css("span.a-price-fraction::text").get()} {response.css("span.a-price-symbol::text").get()}'
    if title and price:
        with open(f'data.txt', 'a+', encoding="utf-8") as file:
            file.write(f"title: {title}\n")
            file.write(f"price: {price}\n")
    else:
        with open(f'data.txt', 'a+', encoding="utf-8") as file:
            file.write(f"ERROR! price: {price} | {title} \n")


def scrape_newegg_item(response, url: None | str = None):
    """
    Scrapes data from a Newegg item page and saves it to the database.

    Args:
        response: The response object containing the HTML of the item page.
        url (optional): The URL of the item page. Defaults to None.

    Notes:
        - This function works only with `newegg.com`.
        - The scraped data includes the title, price, rating, amount of ratings, producer, and class of the item.

    Raises:
        Exception: If there is an error during the scraping process.

    Returns:
        None
    """
    try:
        # ------------------------- Getting data from response -------------------------
        # Extracting item class from breadcrumb
        item_elements = response.css('ol.breadcrumb li a::text').getall()
        item_class = item_elements[-2] if len(item_elements) >= 2 else None

        # Extracting data from JSON-LD script tag
        script_content = response.css('script[type="application/ld+json"]::text').getall()[2]
        parsed_data = json.loads(script_content)

        # Extracting price, title, producer, rating, and amount of ratings
        price = parsed_data.get('offers').get('price')
        title = parsed_data.get('name')
        price_currency = parsed_data.get('offers').get('priceCurrency')
        price += '$' if price_currency == "USD" else ''

        producer = parsed_data.get('brand')
        rating = parsed_data.get('aggregateRating').get('ratingValue')
        amount_of_ratings = parsed_data.get('aggregateRating').get('reviewCount')

        # ------------------------- Processing and saving data from response -------------------------
        save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)
    except Exception as e:
        flash(f"Error: {e}", "danger")


def scrape_gamestop_item(response, url: None | str = None):
    """
Takes title, price, rating, amount of ratings, producer, and class of the item.\n\nWorks only with `gamestop.com`
    """
    # ------------------------- Taking data from response -------------------------

    try:
        script_content = response.css('script[type="application/ld+json"]::text').get()

        parsed_data = json.loads(script_content)

        title = parsed_data.get('name')
        price = parsed_data.get('offers')[0].get('price')
        if parsed_data.get('offers')[0].get('priceCurrency') == "USD":
            price += '$' 
        producer = parsed_data.get('brand')
        item_class = parsed_data.get('category')

        try:
            rating = parsed_data.get('aggregateRating').get('ratingValue')
        except Exception:
            rating = None

        try:
            amount_of_ratings = parsed_data.get('aggregateRating').get('reviewCount')
        except Exception:
            amount_of_ratings = 0

        # ------------------------- Processing and saving data from response -------------------------
        save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)
    except Exception as e:
        flash(f"Error: {e}", "danger")

def scrape_excaliberpc_item(response, url: None | str = None):
    """
    Scrapes data from the ExcaliberPC website and saves it to the database.

    Args:
        response (scrapy.http.Response): The response object containing the web page data.
        url (str, optional): The URL of the web page. Defaults to None.

    Raises:
        Exception: If there is an error during the scraping process.

    Returns:
        None
    """
    try:
        price = response.css('meta[property="price"]::attr(content)').get()
        if response.css('meta[property="priceCurrency"]::attr(content)').get() == "USD":
            price += "$"

        title = response.css('h1.product-head_name::text').get().strip()

        try:
            producer = response.css('meta[property="brand"]::attr(content)').get()
        except Exception:
            producer = None

        try:
            item_class = response.css('ul.breadcrumbs li span::text').getall()[2]
        except Exception:
            item_class = None
        try:
            rating = response.css('meta[property="ratingValue"]::attr(content)').get()
            amount_of_ratings = response.css('meta[property="reviewCount"]::attr(content)').get()
        except Exception:
            rating = None
            amount_of_ratings = 0

        save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)
    except Exception as e:
        flash(f"Error: {e}", "danger")

################### Parsing functions

def parsing_method(response):
    """
    Parses the response object and determines the appropriate scraping method based on the URL domain.

    Args:
        response: The response object obtained from making a request.

    Returns:
        None
    """
    url = response.meta.get('url', '')

    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # html_content = response.body.decode(response.encoding)
    # with open('.html', 'w', encoding=response.encoding) as f:
    #     f.write(html_content)


    if 'ebay' in url:
        scrape_ebay_item(response, url)
    
    elif domain == 'www.amazon.com':
        scrape_amazon_item(response, url)

    elif domain == 'www.amazon.co.uk':
        scrape_amazon_uk_item(response, url)

    elif 'newegg' in url:
        scrape_newegg_item(response, url)

    elif 'gamestop' in url:
        scrape_gamestop_item(response, url)

    elif 'excaliberpc' in url:
        scrape_excaliberpc_item(response, url)