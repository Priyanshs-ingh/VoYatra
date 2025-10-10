# -*- coding: utf-8 -*-
"""
Quick script to run spiders directly with proper settings
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess
from travel_scrapers.spiders.simple_flight_spider import SimpleFlightSpider

if __name__ == '__main__':
    # Manually configure settings to ensure Kafka pipeline is loaded
    settings = {
        'BOT_NAME': 'travel_scrapers',
        'SPIDER_MODULES': ['travel_scrapers.spiders'],
        'NEWSPIDER_MODULE': 'travel_scrapers.spiders',
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': 'INFO',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': True,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        # CRITICAL: Enable Kafka Pipeline
        'ITEM_PIPELINES': {
            'kafka_pipeline.KafkaPipeline': 300,
        },
    }
    
    # Create process with explicit settings
    process = CrawlerProcess(settings)
    
    # Run spider
    process.crawl(SimpleFlightSpider)
    process.start()
