import json
import os
from datetime import datetime
from itemadapter import ItemAdapter

class DataValidationPipeline:
    """Validate scraped data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Basic validation
        if not adapter.get('scraped_at'):
            adapter['scraped_at'] = datetime.now().isoformat()
            
        return item
class FlightItemFilter:
    def __call__(self, item):
        return item.get('data_type') == 'flights'

class NewsItemFilter:
    def __call__(self, item):
        return item.get('data_type') == 'news'

class HotelItemFilter:
    def __call__(self, item):
        return item.get('data_type') == 'hotels'

class WeatherItemFilter:
    def __call__(self, item):
        return item.get('data_type') == 'weather'