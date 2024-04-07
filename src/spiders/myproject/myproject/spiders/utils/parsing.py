"""
This module contains functions for scraping and parsing data from various e-commerce websites.

Functions:
- scrape_amazon_item(response, url=None): Extracts data from the item page in amazon.com.
- scrape_ebay_item(response, url, method="add"): Extracts data from the item page on ebay.com.
- scrape_newegg_item(response, url=None): Scrapes data from a Newegg item page and saves it to the database.
- scrape_gamestop_item(response, url=None): Takes title, price, rating, amount of ratings, producer, and class of the item. Works only with gamestop.com.
- scrape_excaliberpc_item(response, url=None): Scrapes data from the ExcaliberPC website and saves it to the database.
- parsing_method(response): Parses the response object and determines the appropriate scraping method based on the URL domain.
"""

import json
import re
from urllib.parse import urlparse

from .db import save_product_to_database
from .converter import SignsConverter


def scrape_amazon_item(response, url: None | str = None):
    """
    Extracts data from the item page in amazon.com

    Args:
        response (obj): The response object from the web scraping request.
        url (str, optional): The URL of the item page. Defaults to None.

    Returns:
        None

    Raises:
        None`

    Example:
        >>> scrape_amazon_item(response, 'https://www.amazon.com/product')
    """
    try:
        title = response.css("#productTitle::text").get().strip()
        price = float(f'{response.css("span.a-price-whole::text").get().replace(",","")}.{response.css("span.a-price-fraction::text").get()}'.strip())

        price_currency = response.css("span.a-price-symbol::text").get().strip()
        price_currency = SignsConverter.convert_to_country_code(price_currency)

        try:
            image = response.css("div#imgTagWrapperId img::attr(src)").get()
        except Exception:
            image = None
        try:
            rating = float(
                re.findall(r"\d+\.\d+", response.css("span.a-icon-alt::text").get())[0]
            )
            amount_of_ratings = int(
                response.css("a#acrCustomerReviewLink span#acrCustomerReviewText::text")
                .get()
                .strip()
                .replace(",", "")
                .split(" ")[0]
            )
        except Exception:
            rating = None
            amount_of_ratings = 0
        try:
            producer = (
                response.css("tr.po-brand span.po-break-word::text").get().strip()
            )
        except Exception:
            producer = None
        try:
            item_class = (
                response.css("div#wayfinding-breadcrumbs_feature_div ul li")[-1]
                .css("a::text")
                .get()
                .strip()
            )
        except Exception:
            item_class = None

        save_product_to_database(
                url, title, price, price_currency,
                rating, amount_of_ratings,
                item_class, producer, image
            )

    except Exception as e:
        print(f"Error: {e}", "danger")


def scrape_ebay_item(response, url: str, method: str = "add"):
    """
    Extracts data from the item page on `ebay.com`

    Args:
        response: The response object containing the HTML of the item page.
        url (str): The URL of the item page.
        method (str, optional): The method to use when processing the data. Defaults to "add".

    Returns:
        None

    Raises:
        Exception: If there is an error during data extraction.

    """
    try:
        # ------------------------- Taking data from response -------------------------
        script_content = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()[1]
        parsed_data = json.loads(script_content)
        title = parsed_data.get("name")
        price = float(parsed_data.get("offers").get("price"))
        price_currency = parsed_data.get("offers").get("priceCurrency")

        try:
            image = parsed_data.get("image")
        except Exception:
            image = None
        try:
            producer = parsed_data.get("brand").get("name")
        except Exception:
            producer = None
        try:
            item_class = parsed_data.get("category")
        except Exception:
            item_class = None

        try:
            rating = float(response.css("div[data-testid='ux-summary'] span[class='ux-textspans']::text").get())
        except Exception:
            rating = None
        try:
            amount_of_ratings = response.css(
            "div[data-testid='ux-summary'] span[class='ux-summary__count'] span::text"
            ).get()
            print(amount_of_ratings)
            amount_of_ratings = int(amount_of_ratings.split(" ")[0].replace(",", ""))
        except Exception:
            amount_of_ratings = 0

        try:
            print(parsed_data.get("offers").get("availability"))
            if "InStock" in parsed_data.get("offers").get("availability"):
                availability = "In stock"
            else:
                availability = "Out of stock"
        except Exception:
            availability = None

        # ------------------------- Processing and saving data from response -------------------------
        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except Exception as e:
        print(f"Error: {e}", "danger")


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
        # ------------------------- Taking data from response -------------------------
        try:
            item_elements = response.css("ol.breadcrumb li a::text").getall()
            item_class = item_elements[-2] if len(item_elements) >= 2 else None
        except Exception:
            item_class = None
        script_content = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()[2]
        parsed_data = json.loads(script_content)

        price = float(parsed_data.get("offers").get("price"))
        title = parsed_data.get("name")
        price_currency = parsed_data.get("offers").get("priceCurrency")

        try:
            image = parsed_data.get("image")
        except Exception:
            image = None

        try:
            producer = parsed_data.get("brand")
        except Exception:
            producer = None
        try:
            rating = float(
                response.css(
                    "div[data-testid='ux-summary'] span[class='ux-textspans']::text"
                    ).get()
                )

            amount_of_ratings = response.css("div[data-testid='ux-summary'] span[class='ux-textspans']::text").get()
            amount_of_ratings = int(amount_of_ratings.split(" ")[0].replace(",", ""))
        except Exception:
            rating = None
            amount_of_ratings = 0

        # ------------------------- Processing and saving data from response -------------------------
        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image
        )
    except Exception as e:
        print(f"Error: {e}", "danger")


def scrape_gamestop_item(response, url: None | str = None):
    """
    Extracts data from the item page on `gamestop.com` and saves it to the database.

    Args:
        response: The response object containing the HTML of the item page.
        url (optional): The URL of the item page. Defaults to None.

    Raises:
        Exception: If there is an error during the scraping process.

    Returns:
        None
    """

    try:
        # ------------------------- Taking data from response -------------------------
        script_content = response.css('script[type="application/ld+json"]::text').get()

        parsed_data = json.loads(script_content)

        title = parsed_data.get("name")
        price = float(parsed_data.get("offers")[0].get("price"))
        price_currency =  parsed_data.get("offers")[0].get("priceCurrency") 

        producer = parsed_data.get("brand")
        item_class = parsed_data.get("category")

        try:
            image = parsed_data.get("image")
        except Exception:
            image = None

        try:
            rating = parsed_data.get("aggregateRating").get("ratingValue")
        except Exception:
            rating = None

        try:
            amount_of_ratings = parsed_data.get("aggregateRating").get("reviewCount")
        except Exception:
            amount_of_ratings = 0

        try:
            print(parsed_data.get("offers").get("availability"))
            availability = "In stock" if parsed_data.get("offers").get("availability") == "http://schema.org/InStock" else "Out of stock" 
        except Exception:
            availability = None
             

        print(url)
        print(title)
        print(price)
        print(price_currency)
        print(rating)
        print(amount_of_ratings)
        print(item_class)
        print(producer)
        print(image)
        print(availability)


        # ------------------------- Processing and saving data from response -------------------------
        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except Exception as e:
        print(f"Error: {e}", "danger")


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
        price = float(response.css('meta[property="price"]::attr(content)').get())
        price_currency = response.css('meta[property="priceCurrency"]::attr(content)').get()            

        title = response.css("h1.product-head_name::text").get().strip()

        try:
            producer = response.css('meta[property="brand"]::attr(content)').get()
        except Exception:
            producer = None

        try:
            parsed_url = urlparse(url)
            parsed_url.netloc

            image = parsed_url.scheme + "://" + parsed_url.netloc + response.css('img[id="itemphoto"]::attr(src)').get()
        except Exception:
            image = None

        try:
            item_class = response.css("ul.breadcrumbs li span::text").getall()[2]
        except Exception:
            item_class = None
        try:
            rating = response.css('meta[property="ratingValue"]::attr(content)').get()
            amount_of_ratings = response.css(
                'meta[property="reviewCount"]::attr(content)'
            ).get()
        except Exception:
            rating = None
            amount_of_ratings = 0

        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image
        )
    except Exception as e:
        print(f"Error: {e}", "danger")


# Main parsing function

def parsing_method(response):
    """
    Parses the response object and determines the appropriate scraping method based on the URL domain.

    Args:
        response: The response object obtained from making a request.

    Returns:
        None
    """
    url = response.meta.get("url", "")

    html_content = response.body.decode(response.encoding)
    with open(".html", "w", encoding=response.encoding) as f:
        f.write(html_content)

    print(response.meta.get('download_slot'))

    if response.meta.get('download_slot') == "www.ebay.com":
        scrape_ebay_item(response, url)

    elif response.meta.get('download_slot') == "www.amazon.com":
        print("Amazon")
        scrape_amazon_item(response, url)

    elif response.meta.get('download_slot') == "www.amazon.co.uk":
        scrape_amazon_item(response, url)

    elif "newegg" in url:
        scrape_newegg_item(response, url)

    elif "gamestop" in url:
        scrape_gamestop_item(response, url)

    elif "excaliberpc" in url:
        scrape_excaliberpc_item(response, url)
