# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import random

class SimpleFlightSpider(scrapy.Spider):
    """
    Simple test spider for Kafka testing
    """
    name = 'simple_flight'
    
    def start_requests(self):
        # Just one simple request to generate data
        yield scrapy.Request('http://quotes.toscrape.com', self.parse)
    
    def parse(self, response):
        """Generate a few test flights"""
        
        # Generate 3 test flights
        for i in range(3):
            yield {
                'flight_number': f'AI{random.randint(100, 999)}',
                'airline': 'Air India',
                'source': 'Delhi',
                'destination': 'Mumbai',
                'departure_time': '10:30',
                'arrival_time': '12:45',
                'price': 4500.0,
                'duration': '2h 15m',
                'stops': 'Non-stop',
                'scraped_at': datetime.now().isoformat(),
                'url': response.url
            }