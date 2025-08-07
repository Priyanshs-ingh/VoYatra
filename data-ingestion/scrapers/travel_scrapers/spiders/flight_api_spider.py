"""
Alternative Flight Data Sources and Strategies

This module provides multiple strategies to overcome anti-bot measures:

1. API-First Approach: Use official APIs when available
2. Selenium + undetected-chromedriver: Better browser automation
3. Proxy rotation: Rotate IP addresses
4. Alternative data sources: Use less protected sources
"""

import scrapy
import json
import requests
from datetime import datetime, timedelta
from ..items import FlightItem

class FlightDataAPISpider(scrapy.Spider):
    name = 'flight_api_spider'
    
    def __init__(self, origin=None, destination=None, departure_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin or 'DEL'
        self.destination = destination or 'BOM'
        self.departure_date = departure_date or self._get_tomorrow_date()
    
    def _get_tomorrow_date(self):
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    def start_requests(self):
        """Try multiple alternative sources"""
        
        # 1. Amadeus API (requires API key - free tier available)
        yield scrapy.Request(
            url='https://test.api.amadeus.com/v2/shopping/flight-offers',
            callback=self.parse_amadeus,
            meta={'source': 'amadeus_api'}
        )
        
        # 2. Skyscanner RapidAPI (alternative endpoint)
        yield scrapy.Request(
            url='https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/IN/INR/en-US/{}/{}/{}'.format(
                self.origin, self.destination, self.departure_date
            ),
            callback=self.parse_skyscanner_api,
            headers={
                'X-RapidAPI-Host': 'skyscanner-skyscanner-flight-search-v1.p.rapidapi.com',
                'X-RapidAPI-Key': 'YOUR_RAPIDAPI_KEY'  # Replace with actual key
            },
            meta={'source': 'skyscanner_api'}
        )
        
        # 3. Alternative sources - Airport websites, airline direct
        airline_direct_urls = [
            f'https://www.airindia.in/booking/flight-search?origin={self.origin}&destination={self.destination}&departure={self.departure_date}',
            f'https://www.spicejet.com/flight-search?origin={self.origin}&destination={self.destination}&departure={self.departure_date}',
            f'https://www.indigo.in/flight-search?origin={self.origin}&destination={self.destination}&departure={self.departure_date}'
        ]
        
        for url in airline_direct_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_airline_direct,
                meta={'source': 'airline_direct'}
            )
    
    def parse_amadeus(self, response):
        """Parse Amadeus API response"""
        try:
            data = json.loads(response.text)
            for offer in data.get('data', []):
                item = FlightItem()
                item['source'] = 'Amadeus API'
                item['price'] = offer.get('price', {}).get('total', '')
                item['airline'] = offer.get('validatingAirlineCodes', [''])[0]
                # Extract more details...
                yield item
        except Exception as e:
            self.logger.error(f"Amadeus API error: {e}")
    
    def parse_skyscanner_api(self, response):
        """Parse Skyscanner API response"""
        try:
            data = json.loads(response.text)
            for quote in data.get('Quotes', []):
                item = FlightItem()
                item['source'] = 'Skyscanner API'
                item['price'] = quote.get('MinPrice', '')
                # Extract more details...
                yield item
        except Exception as e:
            self.logger.error(f"Skyscanner API error: {e}")
    
    def parse_airline_direct(self, response):
        """Parse airline direct booking sites"""
        # These are usually less protected than aggregators
        pass
