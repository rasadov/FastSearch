from utils import *
from scrapy import *
from myproject.myproject.spiders import MySpider



if __name__ == "__main__":
    spider = MySpider("https://www.amazon.com/b?_encoding=UTF8&tag=593a2799-20&linkCode=ur2&linkId=9a5d2a626ea6c02b657f33f5ed26e741&camp=1789&creative=9325&node=193870011", "url")
    spider.run()
