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
    def google_custom_search(query, start_index,
                        GOOGLE_SEARCH_API=os.environ.get("GOOGLE_SEARCH_ENGINE_API"),
                        GOOGLE_CX=os.environ.get("GOOGLE_CX")
                        ) -> dict | None:
        """
        Searches Google using the Custom Search API.
        """
        base_url = "https://www.googleapis.com/customsearch/v1"
        queries = query if isinstance(query, list) else [query]
        res = []

        for q in queries:
            params = {
                "key": GOOGLE_SEARCH_API,
                "cx": GOOGLE_CX,
                "q": q,
                "start": start_index,
            }

            try:
                response = requests.get(base_url, params=params, timeout=5)
                response.raise_for_status()
                search_results = response.json()
                res.append(search_results)
                print(len(search_results.get("items", [])))
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

        return res if res else None

    @staticmethod
    def search(query: str | list, method: str, total_pages: int | None = None):
        """
        Returns links for the given query and method.
        """
        if method == "google":
            for page in range(1, total_pages + 1):
                start_index = (page - 1) * 10
                try:
                    results = Search.google_custom_search(
                        query, start_index
                    )
                except Exception as e:
                    print(f"An error occurred: {e}")
                    continue

                # Flatten the list of results if necessary
                if isinstance(query, list):
                    results = [item for sublist in results for item in sublist.get("items", [])]

                for result in results:
                    for item in result.get("items", []):
                        link = item.get("link")
                        parsed_url = urlparse(link)
                        link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                        print(link)
                        yield link
        elif method == "url":
            parsed_url = urlparse(query)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL")
            yield f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        else:
            raise ValueError(f"Invalid method: {method}")
