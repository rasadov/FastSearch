from scrapy.crawler import CrawlerProcess
import scrapy
import sys
sys.path.append(r'..\fastsearch')
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
            yield scrapy.Request(url=url, callback=self.parse, meta={'url': url})
    

    def parse(self, response):
        """
Gets the entire HTML content of the page\n
Used to proccess and store data    
        """
        url = response.meta.get('url', '')
        name = ''

        if 'ebay' in url:
            name = scrap_ebay_item(response, url)
        html_content = response.body.decode(response.encoding)
        
        if "amazon" in url:
            with open(f'data.txt', 'a+', encoding="utf-8") as file:
                # file.write(f"Link: {url}, Title: {title}, Price: {price}\n")
                file.write(f"url: {url}\n")
            scrap_amazon_uk_item(response, url)

        # self.log(f'HTML Content: {html_content}')        
        with open(f'{name}.html', 'w', encoding=response.encoding) as f:
            f.write(html_content)
        return None

    def run(self):
        process = CrawlerProcess(
        settings={
            "FEEDS": {
                },
            }
        )
        process.crawl(MySpider, self.query, self.method, self.pages, self.results_per_page)
        process.start()