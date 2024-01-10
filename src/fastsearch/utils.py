import requests
import dotenv
import os

dotenv.load_dotenv()

api_key = os.environ.get("API_KEY") 
cx = os.environ.get("CX") 


def google_custom_search(query, start_index, api_key=api_key, cx=cx):
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
    

def search(query, total_pages):
    for page in range(1, total_pages + 1):
        start_index = (page - 1) * 10
        results = google_custom_search(query, start_index, api_key, cx)
        if results:
            for item in results.get('items', []):
                title = item.get('title')
                link = item.get('link')
                # yield f"Title: {title}\nLink: {link}\n"
                yield title, link


    


if __name__ == "__main__":
    a = [ i for i, k in search('rtx 3060 site:amazon.com', 1)]
    print(a)