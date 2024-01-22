import re
import requests
import dotenv
import json
import os

dotenv.load_dotenv()

api_key = os.environ.get("API_KEY") 
cx = os.environ.get("CX") 


def google_custom_search(query, start_index, api_key=api_key, cx=cx):
    """
    Searches google for query
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cx,
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
    
def custom_url(url):
    """
    For scraping data from single website or if website doesnt have special function for it,\n
    Use `custom_url` function
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        search_results = url
        return search_results
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    

def search(query: str, method: str, total_pages: int | None = None,
           item_class: str | None = None) -> [str, str]:
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
            results = google_custom_search(query, start_index, api_key, cx)
            if results:
                for item in results.get('items', []):
                    title = item.get('title')
                    link = item.get('link')
                    yield title, link

    elif method == 'url':
        yield 'no title for custom url', query

    elif method == 'newegg':
        query = query.split(' ')
        res = ''
        for i in range(len(query)):
            res += i
            if i != len(query) - 1:
                res += "+"
        yield 'no title for this url', f"https://www.newegg.com/p/pl?d={res}"

def scrap_ebay_item(response, url: str):
    """
    Extracts data from the item page on `ebay.com`
    """
    title = response.css('title::text').get()
    price = response.css('div.x-price-primary span.ux-textspans::text').get()

    if title and price:
        with open(f'data.txt', 'a+', encoding="utf-8") as file:
            file.write(f"Link: {url}, Title: {title}, Price: {price}\n")

        name = ''.join(word[0] for word in title.split()[:5])
        return name        

def scrap_amazon_uk_item(response, url: None | str = None):
    """
    Extracts data from item page in amazon.co.uk
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

def scrap_newegg_item(response, url: None | str = None):
    """
Takes title, price, rating, amount of ratings, producer, and class of the item.\n\nWorks only with `newegg.com`  
    """
    # Get data from response
    title = response.css('div.product-wrap h1.product-title::text').get()
    price = response.css('li.price-current strong::text').get() + response.css('li.price-current sup::text').get() + response.css('li.price-current::text').get()
    item_elements = response.css('ol.breadcrumb li a::text').getall()
    rating = response.css('div.product-rating i.rating::attr(title)').get()
    amount_of_ratings = response.css('div.product-rating span.item-rating-num::text').get()
    
    try:
        producer = item_elements[len(item_elements) - 1]
    except IndexError:
        producer = None
    try:
        item_class = item_elements[len(item_elements) - 2]
    except IndexError:
        item_class = None
    
    # Save data to txt file (temporary)
    with open(f'data.txt', 'a+', encoding="utf-8") as file:
        file.write(f"url: {url}\n")
        file.write(f"title: {title}\n")
        file.write(f"price: {price}\n")
        file.write(f"item class: {item_class}\n")
        file.write(f"producer: {producer}\n")
        file.write(f"rating: {rating}\n")
        file.write(f"amount of ratings: {amount_of_ratings}\n")

def scrap_gamestop_item(response, url: None | str = None):
    """
Takes title, price, rating, amount of ratings, producer, and class of the item.\n\nWorks only with `gamestop.com`
    """

    script_content = response.css('script[type="application/ld+json"]::text').get()

    parsed_data = json.loads(script_content)

    # Parse json data
    price = parsed_data.get('offers')[0].get('price')
    if parsed_data.get('offers')[0].get('priceCurrency') == "USD":
        price += '$' 
    producer = parsed_data.get('brand')
    title = parsed_data.get('name')
    item_class = parsed_data.get('category')
    rating = parsed_data.get('aggregateRating').get('ratingValue')
    amount_of_ratings = parsed_data.get('aggregateRating').get('reviewCount')

    
    # Save data to txt file (temporary)
    with open(f'data.txt', 'a+', encoding="utf-8") as file:
        file.write(f"url: {url}\n")
        file.write(f"title: {title}\n")
        file.write(f"price: {price}\n")
        file.write(f"item class: {item_class}\n")
        file.write(f"producer: {producer}\n")
        file.write(f"rating: {rating}\n")
        file.write(f"amount of ratings: {amount_of_ratings}\n")


def parsing_method(response):
    url = response.meta.get('url', '')
    name = ''

    if 'ebay' in url:
        name = scrap_ebay_item(response, url)
    
    elif "amazon" in url:
        with open(f'data.txt', 'a+', encoding="utf-8") as file:
            file.write(f"url: {url}\n")
        scrap_amazon_uk_item(response, url)

    elif 'newegg' in url:
        scrap_newegg_item(response, url)

    elif 'gamestop' in url:
        scrap_gamestop_item(response, url)

    html_content = response.body.decode(response.encoding)
    with open(f'{name}.html', 'w', encoding=response.encoding) as f:
        f.write(html_content)
    
if __name__ == "__main__":
    with open(f'.html', 'r', encoding="utf-8") as file:
        html_content = file.read()