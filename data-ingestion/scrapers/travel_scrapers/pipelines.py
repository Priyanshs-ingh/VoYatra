import json
import os
from datetime import datetime
from itemadapter import ItemAdapter

class DataValidationPipeline:
    """Validate scraped data"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Basic validation
        if not adapter.get('data_type'):
            adapter['data_type'] = spider.name
            
        if not adapter.get('scraped_at'):
            adapter['scraped_at'] = datetime.now().isoformat()
            
        return item

class JsonWriterPipeline:
    """Write items to JSON files"""
    
    def __init__(self):
        self.files = {}
        
    def open_spider(self, spider):
        """Create output directories"""
        data_types = ['flights', 'news', 'hotels', 'weather']
        for data_type in data_types:
            os.makedirs(f'../data/raw/{data_type}', exist_ok=True)
    
    def close_spider(self, spider):
        """Close all files"""
        for file in self.files.values():
            file.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        data_type = adapter.get('data_type', 'unknown')
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'../data/raw/{data_type}/{data_type}_{timestamp}.json'
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Write item to file
        with open(filename, 'a', encoding='utf-8') as f:
            line = json.dumps(dict(adapter), ensure_ascii=False) + '\n'
            f.write(line)
            
        return item

# Item filters for different data types
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