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

import requests
import os
from urllib.parse import urlparse
import dotenv


dotenv.load_dotenv()

GOOGLE_SEARCH_API = os.environ.get("GOOGLE_SEARCH_ENGINE_API")
GOOGLE_CX = os.environ.get("GOOGLE_CX")

class Search():
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
    def google_custom_search(query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX):
        """
        Searches Google using the Custom Search API.

        Args:
            query (str): The search query.
            start_index (int): The index of the first search result to retrieve.
            GOOGLE_SEARCH_API (str): The API key for the Google Custom Search API.
            GOOGLE_CX (str): The custom search engine ID.

        Returns:
            dict: The search results in JSON format.

        Raises:
            requests.exceptions.RequestException: If an error occurs while making the request.

        Example:
            >>> results = google_custom_search('Python', 1)
            >>> print(results['items'][0]['title'])
            'Welcome to Python.org'
        """
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_SEARCH_API,
            "cx": GOOGLE_CX,
            "q": query,
            "start": start_index,
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            return search_results
        except requests.exceptions.RequestException as e:
            return None
        
    @staticmethod
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
        if method == "google":
            for page in range(1, total_pages + 1):
                start_index = (page - 1) * 10
                results = Search.google_custom_search(
                    query, start_index, GOOGLE_SEARCH_API, GOOGLE_CX
                )
                if results:
                    for item in results.get("items", []):
                        link = item.get("link")
                        parsed_url = urlparse(link)
                        link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                        yield link

        elif method == "url":
            parsed_url = urlparse(query)
            query = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            yield query

        else:
            raise ValueError(f"Invalid method: {method}")
