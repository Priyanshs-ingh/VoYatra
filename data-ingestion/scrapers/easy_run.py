# -*- coding: utf-8 -*-
"""
Easy Spider Runner - Run any spider with Kafka enabled
Usage: python easy_run.py <spider_name>
Example: python easy_run.py simple_flight
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapy.crawler import CrawlerProcess

# Import all available spiders
from travel_scrapers.spiders.simple_flight_spider import SimpleFlightSpider
from travel_scrapers.spiders.flights_spider import FlightSpider
from travel_scrapers.spiders.flights_spider_enhanced import FlightsSpiderEnhanced
from travel_scrapers.spiders.amadeus_flight_spider import AmadeusFlightSpider
from travel_scrapers.spiders.hotels_spider import HotelsSpider
from travel_scrapers.spiders.weather_spider import WeatherSpider
from travel_scrapers.spiders.news_spider import NewsSpider

# Map spider names to classes
SPIDERS = {
    'simple_flight': SimpleFlightSpider,
    'flight': FlightSpider,
    'enhanced': FlightsSpiderEnhanced,
    'amadeus': AmadeusFlightSpider,
    'hotels': HotelsSpider,
    'weather': WeatherSpider,
    'news': NewsSpider,
}

def main():
    if len(sys.argv) < 2:
        print("\n🕷️  VoYatra Spider Runner")
        print("=" * 50)
        print("\nUsage: python easy_run.py <spider_name>")
        print("\nAvailable Spiders:")
        print("-" * 50)
        for name, spider_class in SPIDERS.items():
            print(f"  • {name:15} - {spider_class.__doc__ or 'No description'}")
        print("\nExample:")
        print("  python easy_run.py simple_flight")
        print("  python easy_run.py enhanced")
        print()
        sys.exit(1)
    
    spider_name = sys.argv[1].lower()
    
    if spider_name not in SPIDERS:
        print(f"❌ Error: Spider '{spider_name}' not found!")
        print(f"\nAvailable spiders: {', '.join(SPIDERS.keys())}")
        sys.exit(1)
    
    spider_class = SPIDERS[spider_name]
    
    # Configure settings with Kafka pipeline
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
        # Enable Kafka Pipeline
        'ITEM_PIPELINES': {
            'kafka_pipeline.KafkaPipeline': 300,
        },
    }
    
    print(f"\n🚀 Starting spider: {spider_name}")
    print(f"📊 Data will be sent to: Kafka (10.7.6.33:9092)")
    print(f"📝 Topic: flight-data")
    print("=" * 50)
    print()
    
    # Create process with explicit settings
    process = CrawlerProcess(settings)
    
    # Run spider
    process.crawl(spider_class)
    process.start()

if __name__ == '__main__':
    main()
