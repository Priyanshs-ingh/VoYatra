# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
import random

class FlightSpider(scrapy.Spider):
    name = 'flight_spider'
    
    # Example: Scraping from a flight booking website
    # Replace with your actual target website
    start_urls = [
        'https://www.example-flight-booking.com/search?from=Delhi&to=Mumbai'
    ]
    
    def parse(self, response):
        """Parse flight listings from the page"""
        
        # Example selectors - adjust based on your target website
        flights = response.css('div.flight-item')
        
        for flight in flights:
            yield {
                'flight_number': flight.css('span.flight-number::text').get(),
                'airline': flight.css('span.airline-name::text').get(),
                'source': flight.css('span.departure-city::text').get(),
                'destination': flight.css('span.arrival-city::text').get(),
                'departure_time': flight.css('span.departure-time::text').get(),
                'arrival_time': flight.css('span.arrival-time::text').get(),
                'price': float(flight.css('span.price::text').re_first(r'[\d,]+').replace(',', '')),
                'duration': flight.css('span.duration::text').get(),
                'stops': flight.css('span.stops::text').get(),
                'scraped_at': datetime.now().isoformat(),
                'url': response.url
            }
        
        # Follow pagination if exists
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)