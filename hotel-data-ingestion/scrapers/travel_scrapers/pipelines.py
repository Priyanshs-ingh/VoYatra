# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re
from datetime import datetime
from itemadapter import ItemAdapter
from travel_scrapers.items import BookingHotelItem


class BookingPipeline:
    """Pipeline to process Booking.com hotel items"""
    
    def __init__(self):
        self.items_count = 0
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if isinstance(item, BookingHotelItem):
            # Clean and validate data
            self.clean_price_data(adapter)
            self.clean_rating_data(adapter)
            self.clean_text_fields(adapter)
            self.validate_required_fields(adapter)
            
            self.items_count += 1
            spider.logger.info(f"Processed hotel item #{self.items_count}: {adapter.get('name')}")
            
        return item
    
    def clean_price_data(self, adapter):
        """Clean price-related fields"""
        # Clean price text
        price = adapter.get('price')
        if price:
            # Remove extra whitespace and currency symbols
            cleaned_price = re.sub(r'[^\d,.\s]', '', str(price))
            adapter['price'] = cleaned_price.strip()
        
        # Ensure price_numeric is a number
        price_numeric = adapter.get('price_numeric')
        if price_numeric is not None:
            try:
                adapter['price_numeric'] = float(price_numeric)
            except (ValueError, TypeError):
                adapter['price_numeric'] = None
                
    def clean_rating_data(self, adapter):
        """Clean rating and review fields"""
        # Clean rating
        rating = adapter.get('rating')
        if rating:
            # Extract numeric rating
            rating_match = re.search(r'(\d+\.?\d*)', str(rating))
            if rating_match:
                try:
                    adapter['rating_numeric'] = float(rating_match.group(1))
                except ValueError:
                    adapter['rating_numeric'] = None
        
        # Clean review count
        reviews_count = adapter.get('reviews_count')
        if reviews_count:
            # Extract numeric count
            reviews_match = re.search(r'([\d,]+)', str(reviews_count).replace(',', ''))
            if reviews_match:
                try:
                    adapter['reviews_count_numeric'] = int(reviews_match.group(1))
                except ValueError:
                    adapter['reviews_count_numeric'] = None
                    
    def clean_text_fields(self, adapter):
        """Clean text fields"""
        text_fields = ['name', 'location']
        
        for field in text_fields:
            value = adapter.get(field)
            if value:
                # Remove extra whitespace and special characters
                cleaned_value = re.sub(r'\s+', ' ', str(value).strip())
                cleaned_value = re.sub(r'[\xa0\u200b\u200c\u200d\ufeff]', '', cleaned_value)
                adapter[field] = cleaned_value
                
    def validate_required_fields(self, adapter):
        """Validate that required fields are present"""
        required_fields = ['name']
        
        for field in required_fields:
            if not adapter.get(field):
                raise ValueError(f"Missing required field: {field}")
                
    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f"Pipeline processed {self.items_count} hotel items")


class JsonWriterPipeline:
    """Pipeline to write items to JSON file"""
    
    def __init__(self):
        self.file = None
        self.items = []
        
    def open_spider(self, spider):
        """Called when spider opens"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"booking_hotels_{spider.destination}_{timestamp}.json"
        self.file = open(filename, 'w', encoding='utf-8')
        
    def close_spider(self, spider):
        """Called when spider closes"""
        if self.file:
            json.dump(self.items, self.file, ensure_ascii=False, indent=2)
            self.file.close()
            spider.logger.info(f"Saved {len(self.items)} items to JSON file")
            
    def process_item(self, item, spider):
        """Process each item"""
        self.items.append(dict(item))
        return item


class DuplicatesPipeline:
    """Pipeline to filter duplicate items"""
    
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Use hotel ID or name as unique identifier
        hotel_id = adapter.get('id') or adapter.get('name')
        
        if hotel_id in self.ids_seen:
            spider.logger.warning(f"Duplicate item found: {hotel_id}")
            raise ValueError("Duplicate item")
        else:
            self.ids_seen.add(hotel_id)
            return item

