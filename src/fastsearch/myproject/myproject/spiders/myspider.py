from scrapy.crawler import CrawlerProcess
import scrapy
import sys
sys.path.append(r'..\fastsearch')
from utils import *
import warnings


warnings.filterwarnings("ignore", category=scrapy.exceptions.ScrapyDeprecationWarning)


class MySpider(scrapy.Spider):
    """Spider recieves and processes requests\n"""
    name = 'myspider'
    start_urls = []
    def __init__(self, query: str, method:str, pages = None, results_per_page = None) -> None:
        self.query = query
        self.method = method
        self.pages = pages
        self.results_per_page = results_per_page

    def start_requests(self):
        self.start_urls = [link for title, link in search(self.query, self.method, self.pages)]
        try:
            self.start_urls = self.start_urls[:self.results_per_page]
        except IndexError:
            pass

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'url': url})
    

    def parse(self, response):
        """
Gets the entire HTML content of the page\n
Used to proccess and store data    
        """
        parsing_method(response)

    def run(self):
        """Activates spider:\n
    Scraps data and stores it"""
        process = CrawlerProcess(
        settings={
            "FEEDS": {
                },
            }
        )
        process.crawl(MySpider, self.query, self.method, self.pages, self.results_per_page)
        process.start()