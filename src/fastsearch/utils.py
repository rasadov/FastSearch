import requests
import dotenv
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
    If website you are using doesn't have special funtion for it,\n
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
    

def search(query: str, method: str, total_pages: int | None = None) -> [str, str]:
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

def scrap_ebay_item(response, url: str):
    """
    Extracts data from the item page on ebay
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
        # for i in price:
            with open(f'data.txt', 'a+', encoding="utf-8") as file:
                # file.write(f"Link: {url}, Title: {title}, Price: {price}\n")
                file.write(f"title: {title}\n")
                file.write(f"price: {price}\n")
    else:
        with open(f'data.txt', 'a+', encoding="utf-8") as file:
                # file.write(f"Link: {url}, Title: {title}, Price: {price}\n")
                file.write(f"ERROR! price: {price} | {title} \n")


if __name__ == "__main__":
    with open(f'.html', 'r', encoding="utf-8") as file:
        html_content = file.read()