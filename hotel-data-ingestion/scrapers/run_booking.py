#!/usr/bin/env python3

import sys
import os
from scrapy.crawler import CrawlerProcess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the spider
from travel_scrapers.spiders.booking_spider import BookingSpider

def main():
    # Set up Scrapy settings with more debugging
    settings = {
        'BOT_NAME': 'travel_scrapers',
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        },
        'ITEM_PIPELINES': {
            'travel_scrapers.pipelines.BookingPipeline': 300,
        },
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 15,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'FEEDS': {
            'booking_hotels_%(time)s.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
            }
        },
        'LOG_LEVEL': 'DEBUG',  # More verbose logging
        # Save the response for debugging
        'DOWNLOADER_MIDDLEWARES': {
            'travel_scrapers.middlewares.ResponseSaverMiddleware': 500,
        }
    }
    
    # Configure the process
    process = CrawlerProcess(settings)
    
    # Add the spider to the process
    process.crawl(BookingSpider, destination="Mumbai", checkin="2025-08-20", checkout="2025-08-22")
    
    # Start the crawling
    process.start()

if __name__ == '__main__':
    main()
