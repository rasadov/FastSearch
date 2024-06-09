"""
This file contains the implementation of a Search class that provides 
methods for searching and retrieving links based on a query and method.

The Search class has the following methods:
- `google_custom_search(query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX)`: 
Searches Google using the Custom Search API.
- `search(query, method, total_pages=None)`: Returns links for the given query and method.

The Search class does not have any attributes.

Example usage:
    search_obj = Search()
    results = search_obj.google_custom_search('Python', 1, GOOGLE_SEARCH_API, GOOGLE_CX)
    for link in search_obj.search('python', 'google', total_pages=3):
        print(link)
"""

import os
from urllib.parse import urlparse

import requests
import dotenv

dotenv.load_dotenv()

class Search:
    """
    A class that provides methods for searching and retrieving links based on a query and method.

    Methods:
        google_custom_search(query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX):
            Searches Google using the Custom Search API.

        search(query, method, total_pages=None):
            Returns links for the given query and method.

    Attributes:
        None
    """

    @staticmethod
    def google_query_search(query, start_index,
                            GOOGLE_SEARCH_API = os.getenv("GOOGLE_SEARCH_ENGINE_API"),
                            GOOGLE_CX = os.getenv("GOOGLE_CX")):
        """
        Searches Google using the Custom Search API.
        """
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_SEARCH_API,
            "cx": GOOGLE_CX,
            "q": query,
            "start": start_index,
        }

        try:
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            search_results = response.json()
            return search_results
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def google_list_search(queryList: list, total_pages: int = 1):
        for page in range(1, total_pages + 1):
            start_index = (page - 1) * 10
            for query in queryList:
                try:
                    results = Search.google_query_search(
                        query, start_index
                    )
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue

                for item in results.get("items", []):
                    link = item.get("link")
                    parsed_url = urlparse(link)
                    link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    yield link

    @staticmethod
    def url_search(url: str):
        """
        Returns the URL if it is valid. 
        """
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL")
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    @staticmethod
    def search(query: str | list, method: str, total_pages: int | None = None):
        """
        Returns links for the given parameters.
        """
        if method == "google":
            yield from Search.google_list_search(query, total_pages)

        elif method == "url":
            yield Search.url_search(query)

        else:
            raise ValueError(f"Invalid method: {method}")
