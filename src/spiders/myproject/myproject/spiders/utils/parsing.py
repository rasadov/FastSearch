"""
This module contains functions for scraping and parsing data from various e-commerce websites.

Functions:
- scrape_amazon_item(response: Response, url=None):
Extracts data from the item page in amazon.com.
- scrape_ebay_item(response: Response, url=None):
Extracts data from the item page on ebay.com.
- scrape_newegg_item(response: Response, url=None):
Extracts data from the item page on newegg.com.
- scrape_gamestop_item(response: Response, url=None):
Extracts data from the item page on gamestop.com.
- scrape_excaliberpc_item(response: Response, url=None):
Extracts data from the item page on excaliberpc.com.
- parsing_method(response: Response):
Parses the response object and determines the appropriate scraping method based on the URL domain.
"""

import json
import re
from urllib.parse import urlparse
from scrapy.http import Response

from spiders.myproject.myproject.spiders.utils.db import (save_product_to_database,
                                                          deactivate_product)
from spiders.myproject.myproject.spiders.utils.converter import SignsConverter


def scrape_amazon_item(response: Response, url: None | str = None):
    """
    Extracts data from the item page in amazon.com and saves it to the database.

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
        price_whole = response.css("span.a-price-whole::text").get().replace(",","")
        price_fraction = response.css("span.a-price-fraction::text").get()
        price = float(
            f'{price_whole}.{price_fraction}'.strip())

        price_currency = response.css("span.a-price-symbol::text").get().strip()
        price_currency = SignsConverter.convert_to_country_code(price_currency)

        image = response.css("div#imgTagWrapperId img::attr(src)").get()
        
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
        except (AttributeError, IndexError, ValueError):
            rating = None
            amount_of_ratings = 0
        try:
            producer = (
                response.css("tr.po-brand span.po-break-word::text").get().strip()
            )
        except AttributeError:
            producer = None
        try:
            item_class = (
                response.css("div#wayfinding-breadcrumbs_feature_div ul li")[-1]
                .css("a::text")
                .get()
                .strip()
            )
        except (IndexError, AttributeError):
            item_class = None

        availability = "In stock"

        save_product_to_database(
                url, title, price, price_currency,
                rating, amount_of_ratings,
                item_class, producer, image, availability
            )

    except (AttributeError, ValueError) as e:
        print(f"Error: {e}")
        deactivate_product(url)



def scrape_ebay_item(response: Response, url: str):
    """
    Extracts data from the item page on `ebay.com` and saves it to the database.

    Args:
        response: The response object containing the HTML of the item page.
        url (str): The URL of the item page.

    Returns:
        None

    Raises:
        Exception: If there is an error during data extraction.

    """
    try:
        script_content = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()[1]
        parsed_data = json.loads(script_content)
        title = parsed_data.get('name')
        price_info = parsed_data.get('mainEntity', {}).get('offers', {}).get(
            'itemOffered', [{}])[0].get('offers', [None, {}])[1]
        price = price_info.get('price')
        price_currency = price_info.get('priceCurrency')

        try:
            image = parsed_data.get('mainEntity', {}).get('offers', {}).get(
                'itemOffered', [{}])[0].get('image')
        except (IndexError, AttributeError):
            image = None
        try:
            producer = parsed_data.get('mainEntity', {}).get('offers', {}).get(
                'itemOffered', [{}])[0].get('brand')
        except (IndexError, AttributeError):
            producer = None
        
        item_class = parsed_data.get("category")


        try:
            rating_info = parsed_data.get('mainEntity', {}).get('offers', {}).get(
                'itemOffered', [{}])[0].get('aggregateRating', {})
            rating = float(rating_info.get('ratingValue'))
            amount_of_ratings = int(rating_info.get('reviewCount'))
        except (ValueError, AttributeError, IndexError):
            rating = None
            amount_of_ratings = 0

        try:
            availability = "In stock" if "InStock" in parsed_data.get(
                'mainEntity', {}).get('offers', {}).get('availability', "") else "Out of stock"
        except AttributeError:
            availability = None

        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except (ValueError, AttributeError, IndexError) as e:
        print(f"Error: {e}")
        deactivate_product(url)


def scrape_newegg_item(response: Response, url: None | str = None):
    """
    Extracts data from the item page on `newegg.com` and saves it to the database.

    Args:
        response: The response object containing the HTML of the item page.
        url (optional): The URL of the item page. Defaults to None.

    Notes:
        - This function works only with `newegg.com`.
        - The scraped data includes the title, price, rating, amount of ratings, 
        producer, and class of the item.

    Raises:
        Exception: If there is an error during the scraping process.

    Returns:
        None
    """
    try:
        try:
            item_elements = response.css("ol.breadcrumb li a::text").getall()
            item_class = item_elements[-2] if len(item_elements) >= 2 else None
        except IndexError:
            item_class = None
        script_content = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()[2]
        parsed_data = json.loads(script_content)

        price = float(parsed_data.get("offers").get("price"))
        title = parsed_data.get("name")
        price_currency = parsed_data.get("offers").get("priceCurrency")

        image = parsed_data.get("image")

        producer = parsed_data.get("brand")

        try:
            rating = float(
                parsed_data.get("aggregateRating").get("ratingValue")
                )

            amount_of_ratings = int(
                parsed_data.get("aggregateRating").get("reviewCount")
            )
        except (ValueError, AttributeError):
            rating = None
            amount_of_ratings = 0

        try:
            if parsed_data.get("offers").get("availability") in [
                "https://schema.org/InStock","http://schema.org/InStock"
                ]:
                availability = "In stock"
            else:
                availability = "Out of stock"
        except AttributeError:
            availability = None        

        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except (AttributeError, ValueError) as e:
        print(f"Error: {e}")
        deactivate_product(url)


def scrape_gamestop_item(response: Response, url: None | str = None):
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
        script_content = response.css('script[type="application/ld+json"]::text').get()

        parsed_data = json.loads(script_content)

        title = parsed_data.get("name")
        price = float(parsed_data.get("offers")[0].get("price"))
        price_currency =  parsed_data.get("offers")[0].get("priceCurrency") 

        producer = parsed_data.get("brand")

        item_class = parsed_data.get("category")
    
        image = parsed_data.get("image")

        try:
            rating = parsed_data.get("aggregateRating").get("ratingValue")
        except AttributeError:
            rating = None

        try:
            amount_of_ratings = parsed_data.get("aggregateRating").get("reviewCount")
        except AttributeError:
            amount_of_ratings = 0

        try:
            availability = "In stock" if parsed_data.get("offers").get("availability") in [
                "https://schema.org/InStock","http://schema.org/InStock"] else "Out of stock"
        except AttributeError:
            availability = None

        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except (AttributeError, IndexError, ValueError) as e:
        print(f"Error: {e}")
        deactivate_product(url)


def scrape_excaliberpc_item(response: Response, url: None | str = None):
    """
    Extracts data from the item page on `excaliberpc.com` and saves it to the database.

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

        producer = response.css('meta[property="brand"]::attr(content)').get()

        image_url = response.css('img[id="itemphoto"]::attr(src)').get()

        if image_url:
            parsed_url = urlparse(url)
            parsed_url.netloc


            image = parsed_url.scheme + "://" + parsed_url.netloc + image_url
        else:
            image = None


        try:
            item_class = response.css("ul.breadcrumbs li span::text").getall()[2]
        except IndexError:
            item_class = None

        rating = response.css('meta[property="ratingValue"]::attr(content)').get()
        amount_of_ratings = response.css(
            'meta[property="reviewCount"]::attr(content)'
        ).get()

        availability = response.css('link[property="availability"]::attr(href)').get()
        availability = "In stock" if availability in [
            "https://schema.org/InStock","http://schema.org/InStock"] else "Out of stock"

        save_product_to_database(
            url, title, price, price_currency,
            rating, amount_of_ratings,
            item_class, producer, image, availability
        )
    except (AttributeError, ValueError) as e:
        print(f"Error: {e}")
        deactivate_product(url)


# Main parsing function

def parsing_method(response: Response) -> None:
    """
    Parses the response object and determines the appropriate scraping method
    based on the URL domain.

    Args:
        response: The response object obtained from making a request.

    Returns:
        None
    """
    url = response.meta.get("url", "")

    # html_content = response.body.decode(response.encoding)
    # with open(".html", "w", encoding=response.encoding) as f:
    #     f.write(html_content)

    if response.meta.get('download_slot') == "www.ebay.com":
        scrape_ebay_item(response, url)

    elif response.meta.get('download_slot') == "www.amazon.com":
        scrape_amazon_item(response, url)

    elif response.meta.get('download_slot') == "www.amazon.co.uk":
        scrape_amazon_item(response, url)

    elif "newegg" in url:
        scrape_newegg_item(response, url)

    elif "gamestop" in url:
        scrape_gamestop_item(response, url)

    elif "excaliberpc" in url:
        scrape_excaliberpc_item(response, url)
