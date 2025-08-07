# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookingHotelItem(scrapy.Item):
    """Item for Booking.com hotel data"""
    # Basic hotel information
    id = scrapy.Field()
    name = scrapy.Field()
    location = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    page_name = scrapy.Field()
    
    # Pricing information
    price = scrapy.Field()
    price_numeric = scrapy.Field()
    currency = scrapy.Field()
    
    # Rating and reviews
    rating = scrapy.Field()
    rating_numeric = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews_count_numeric = scrapy.Field()
    
    # Additional metadata
    source = scrapy.Field()  # 'html' or 'graphql'
    scraped_at = scrapy.Field()
    search_destination = scrapy.Field()
    search_checkin = scrapy.Field()
    search_checkout = scrapy.Field()


class BookingHotelDetailsItem(scrapy.Item):
    """Item for detailed hotel information"""
    hotel_id = scrapy.Field()
    description = scrapy.Field()
    address = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    amenities = scrapy.Field()
    facilities = scrapy.Field()
    room_types = scrapy.Field()
    photos = scrapy.Field()
    
    
class BookingReviewItem(scrapy.Item):
    """Item for hotel reviews"""
    hotel_id = scrapy.Field()
    review_id = scrapy.Field()
    reviewer_name = scrapy.Field()
    reviewer_country = scrapy.Field()
    rating = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    date = scrapy.Field()
    language = scrapy.Field()


class BookingPriceItem(scrapy.Item):
    """Item for pricing calendar data"""
    hotel_id = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    available = scrapy.Field()
    min_stay = scrapy.Field()
    