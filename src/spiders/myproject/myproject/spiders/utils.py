"""
This module contains functions for searching, parsing and saving data to the database.

Functions:
    search functions for spider: search, google_custom_search
    database functions for storing scraped data: save_product_to_database
    parsing functions for spider: scrap_ebay_item, scrap_amazon_uk_item, scrap_newegg_item, scrap_gamestop_item, scrap_excaliberpc_item, parsing_method

"""

import psycopg2
import dotenv
import os
import re
import requests
import json
from urllib.parse import urlparse


dotenv.load_dotenv()

GOOGLE_SEARCH_API = os.environ.get("GOOGLE_SEARCH_ENGINE_API") 
GOOGLE_CX = os.environ.get("GOOGLE_CX")

DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')


################### Search functions

def google_custom_search(query, start_index):
    """
    Searches google for query
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
        print(f"Error: {e}")
        return None

def search(query: str, method: str, total_pages: int | None = None):
    """
Returns link for the page\n
`query`
    Url or query you want to search for\n
`method`
    Website you are going to use\n
`total_pages`
    amount of pages you will get links from\n
If it is one page website, no need to set `total_pages` parameter
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

    elif method == 'newegg':
        query = query.split(' ')
        res = ''
        for i in range(len(query)):
            res += i
            if i != len(query) - 1:
                res += "+"
        yield f"https://www.newegg.com/p/pl?d={res}"

################### Database functions

def save_product_to_database(url, title, price, rating = None, amount_of_ratings = None, item_class = None, producer = None):
    """Checks if product is already in database:\n
    If yes, then checks for change in price/rating:\n 
    \tIf price changed, updates data in `product` table and saves price change in `price_history` table.\n
    \tIf rating has changed updates record in the `product` table\n
    Else:\n
    \tAdds new record in `product` table and starts tracking the price in `price_history` table"""

    url = urlparse(url).netloc + urlparse(url).path  # Shortening url to avoid duplicates in the database

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
            print(f"Product with URL {url} updated.")
        else:
            print(f"Product with URL {url} already exists in the database, no update needed.")
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
        
        print(f"New product with URL {url} inserted into the database.")

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
    """
    title = response.css('#productTitle::text').get().strip()
    price = f'{response.css("span.a-price-whole::text").get()}.{response.css("span.a-price-fraction::text").get()} {response.css("span.a-price-symbol::text").get()}'.strip()
    rating = float(re.findall(r'\d+\.\d+', response.css("span.a-icon-alt::text").get())[0])
    amount_of_ratings = int(response.css("a#acrCustomerReviewLink span#acrCustomerReviewText::text").get().strip().replace(',', '').split(' ')[0])
    producer = response.css('tr.po-brand span.po-break-word::text').get().strip()
    item_class = response.css("div#wayfinding-breadcrumbs_feature_div ul li")[-1].css("a::text").get().strip()

    save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)


    

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
Takes title, price, rating, amount of ratings, producer, and class of the item.\n\nWorks only with `newegg.com`  
    """
    # ------------------------- Getting data from response -------------------------
    item_elements = response.css('ol.breadcrumb li a::text').getall()
    try:
        item_class = item_elements[len(item_elements) - 2]
    except IndexError:
        item_class = None
    

    script_content = response.css('script[type="application/ld+json"]::text').getall()[2]

    parsed_data = json.loads(script_content)

    price = parsed_data.get('offers').get('price')
    if parsed_data.get('offers').get('priceCurrency') == "USD":
        price += '$' 
    producer = parsed_data.get('brand')
    title = parsed_data.get('name')

    rating = parsed_data.get('aggregateRating').get('ratingValue')
    amount_of_ratings = parsed_data.get('aggregateRating').get('reviewCount')
    
    # ------------------------- Processing and saving data from response -------------------------
    save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)

def scrape_gamestop_item(response, url: None | str = None):
    """
Takes title, price, rating, amount of ratings, producer, and class of the item.\n\nWorks only with `gamestop.com`
    """
    # ------------------------- Taking data from response -------------------------
    script_content = response.css('script[type="application/ld+json"]::text').get()

    parsed_data = json.loads(script_content)

    with open("Sample.json", "+a", encoding="utf-8") as file:
        file.writelines(script_content)

    title = parsed_data.get('name')
    price = parsed_data.get('offers')[0].get('price')
    if parsed_data.get('offers')[0].get('priceCurrency') == "USD":
        price += '$' 
    producer = parsed_data.get('brand')
    item_class = parsed_data.get('category')

    rating = parsed_data.get('aggregateRating')
    if rating:
        rating = rating.get('ratingValue')

    amount_of_ratings = parsed_data.get('aggregateRating')
    if amount_of_ratings:
        amount_of_ratings = amount_of_ratings.get('reviewCount')
    
    # ------------------------- Processing and saving data from response -------------------------
    save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)

def scrape_excaliberpc_item(response, url : None | str = None):
    # ------------------------- Taking data from response -------------------------
    price = response.css('meta[property="price"]::attr(content)').get()
    if response.css('meta[property="priceCurrency"]::attr(content)').get() == "USD":
        price += "$"

    producer = response.css('meta[property="brand"]::attr(content)').get()
    title = response.css('h1.product-head_name::text').get().strip()
    
    item_class = response.css('ul.breadcrumbs li span::text').getall()[2]
    rating = response.css('meta[property="ratingValue"]::attr(content)').get()
    amount_of_ratings = response.css('meta[property="reviewCount"]::attr(content)').get()

    # ------------------------- Processing and saving data from response -------------------------
    save_product_to_database(url, title, price, rating, amount_of_ratings, item_class, producer)

def parsing_method(response):
    url = response.meta.get('url', '')

    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    html_content = response.body.decode(response.encoding)
    with open('.html', 'w', encoding=response.encoding) as f:
        f.write(html_content)


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