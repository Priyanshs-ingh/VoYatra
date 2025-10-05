# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import random

class TestFlightSpider(scrapy.Spider):
    """
    Simple test spider that generates fake flight data
    Use this to test Kafka pipeline without actual scraping
    """
    name = 'test_flight_spider'
    
    def start_requests(self):
        # Generate fake flight data for testing
        yield scrapy.Request('http://quotes.toscrape.com', self.parse)
    
    def parse(self, response):
        """Generate test flight data"""
        
        airlines = ['Air India', 'IndiGo', 'SpiceJet', 'Vistara', 'GoAir']
        routes = [
            ('Delhi', 'Mumbai'),
            ('Bangalore', 'Hyderabad'),
            ('Chennai', 'Kolkata'),
            ('Pune', 'Goa')
        ]
        
        # Generate 10 test flights
        for i in range(10):
            source, destination = random.choice(routes)
            
            yield {
                'flight_number': f'{random.choice(["AI", "6E", "SG", "UK", "G8"])}{random.randint(100, 999)}',
                'airline': random.choice(airlines),
                'source': source,
                'destination': destination,
                'departure_time': f'{random.randint(6, 22):02d}:{random.choice(["00", "30"])}',
                'arrival_time': f'{random.randint(8, 23):02d}:{random.choice(["00", "30"])}',
                'price': round(random.uniform(3000, 15000), 2),
                'duration': f'{random.randint(1, 4)}h {random.randint(0, 55)}m',
                'stops': random.choice(['Non-stop', '1 stop', '2 stops']),
                'scraped_at': datetime.now().isoformat(),
                'url': response.url
            }