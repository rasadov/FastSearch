from typing import Any, Optional
from scrapy.crawler import CrawlerProcess
import scrapy
import sys
sys.path.append(r'C:\Users\RAUF\Desktop\Github_works\FastSearch\src\fastsearch')
from utils import search

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = []
    def __init__(self, query, pages):
        self.query = query
        self.pages = pages


    def start_requests(self):
        self.start_urls = [link for title, link in search(self.query, self.pages)]
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    

    def parse(self, response):
        # Get the entire HTML content of the page
        title = response.css('title::text').get()
        html_content = response.body.decode(response.encoding)

        # Do something with the HTML content
        self.log(f'HTML Content: {html_content}')
        
        # If you want to save the HTML content to a file, you can use the following:
        i = 0
        with open(f'fr.html', 'w', encoding=response.encoding) as f:
            f.write(html_content)

    def run(self):
        process = CrawlerProcess(
        settings={
            "FEEDS": {
                "items.json": {"format": "json"},
                },
            }
        )
        process.crawl(MySpider, self.query, self.pages)
        process.start()