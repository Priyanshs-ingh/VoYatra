import scrapy

class FlightItem(scrapy.Item):
    """Flight data item"""
    origin = scrapy.Field()
    destination = scrapy.Field()
    departure_date = scrapy.Field()
    return_date = scrapy.Field()
    airline = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    duration = scrapy.Field()
    stops = scrapy.Field()
    departure_time = scrapy.Field()
    arrival_time = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
    data_type = scrapy.Field()

class NewsItem(scrapy.Item):
    """News data item"""
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    published_date = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    scraped_at = scrapy.Field()
    data_type = scrapy.Field()

class HotelItem(scrapy.Item):
    """Hotel data item"""
    name = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    rating = scrapy.Field()
    amenities = scrapy.Field()
    check_in_date = scrapy.Field()
    check_out_date = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
    data_type = scrapy.Field()

class WeatherItem(scrapy.Item):
    """Weather data item"""
    location = scrapy.Field()
    temperature = scrapy.Field()
    humidity = scrapy.Field()
    weather_condition = scrapy.Field()
    forecast_date = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
    data_type = scrapy.Field()