from typing import Any, Optional
from scrapy.crawler import CrawlerProcess
import scrapy
import sys
sys.path.append(r'C:\Users\RAUF\Desktop\Github_works\FastSearch\src\fastsearch')
from utils import *
import warnings


warnings.filterwarnings("ignore", category=scrapy.exceptions.ScrapyDeprecationWarning)


class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = []
    def __init__(self, query, method, pages=None, results_per_page = None):
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
            yield scrapy.Request(url=url, callback=lambda response: self.parse(response=response, url=url))
    

    def parse(self, response, url):
        """
Gets the entire HTML content of the page\n
Used to proccess and store data    
        """
        if 'ebay' in url:
            scrap_ebay_item(response, url)
        html_content = response.body.decode(response.encoding)

        # self.log(f'HTML Content: {html_content}')        
        with open(f'sadsad.html', 'w', encoding=response.encoding) as f:
            f.write(html_content)
        return None

    def run(self):
        process = CrawlerProcess(
        settings={
            "FEEDS": {
                "items.json": {"format": "json"},
                },
            }
        )
        process.crawl(MySpider, self.query, self.method, self.pages, self.results_per_page)
        process.start()