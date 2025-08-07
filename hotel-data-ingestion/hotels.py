import scrapy


class HotelsSpider(scrapy.Spider):
    name = "hotels"
    allowed_domains = ["trivago.in"]
    start_urls = ["https://trivago.in"]

    def parse(self, response):
        pass
