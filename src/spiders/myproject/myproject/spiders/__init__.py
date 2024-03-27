"""
This module contains the spider class for web scraping.
~~~~~~~~~~~~~~~~~~~~~

The spider class, MySpider, is responsible for receiving and processing requests to scrape data from web pages. It utilizes the Scrapy framework to perform the scraping operation.

Example usage:
    spider = MySpider(query='scrapy', method='url', pages=5, results_per_page=10)
    spider.run()

Attributes:
    name (str): The name of the spider.
    start_urls (list): The list of URLs to start scraping from.

Args:
    query (str): The search query to be used for scraping.
    method (str): The method to be used for scraping, e.g., 'url', 'api'.
    pages (int): The number of pages to scrape.
    results_per_page (int): The number of results to scrape per page.

Methods:
    start_requests(): Generates the initial requests to start scraping.
    parse(response): Parses the response and extracts data from the web page.
    run(): Activates the spider and starts the scraping process.

"""

import warnings

import scrapy
from scrapy.crawler import CrawlerProcess

from .utils.parsing import parsing_method
from .progress import send_progress
from .utils.search import Search

warnings.filterwarnings("ignore", category=scrapy.exceptions.ScrapyDeprecationWarning)


class MySpider(scrapy.Spider):
    """
    Spider class for web scraping.

    This class receives and processes requests to scrape data from web pages. It inherits from the Scrapy Spider class.

    Attributes:
        name (str): The name of the spider.
        start_urls (list): The list of URLs to start scraping from.

    Args:
        query (str): The search query to be used for scraping.
        method (str): The method to be used for scraping, e.g., 'url', 'api'.
        pages (int): The number of pages to scrape.
        results_per_page (int): The number of results to scrape per page.

    """

    name = "myspider"
    start_urls = []
    progress = 0
    estimated = 0

    def __init__(
        self, query: str = "", method: str = "url", pages=None, results_per_page=None
    ) -> None:
        self.query = query
        self.method = method
        self.pages = pages
        self.results_per_page = results_per_page

    def start_requests(self):
        """
        Generates the initial requests to start scraping.

        Returns:
            generator: A generator of scrapy.Request objects.

        """
        self.start_urls = [link for link in Search.search(self.query, self.method, self.pages)]
        self.estimated = len(self.start_urls)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"url": url})

    def parse(self, response):
        """
        Parses the response and extracts data from the web page.

        Args:
            response (scrapy.http.Response): The response object containing the HTML content of the page.

        """
        try:
            parsing_method(response)
            self.progress += 1
            send_progress(self)
        except Exception:
            pass

    def get_progress(self):
        """
        Returns the progress of the scraping process.

        Returns:
            tuple: The progress and estimated number of pages to be scraped.

        """
        return self.progress, self.estimated

    def run(self):
        """
        Activates the spider and starts the scraping process.

        This method creates a CrawlerProcess object and starts the spider.

        """
        process = CrawlerProcess(
            settings={
                "FEEDS": {},
            }
        )
        process.crawl(
            MySpider, self.query, self.method, self.pages, self.results_per_page
        )
        process.start()
