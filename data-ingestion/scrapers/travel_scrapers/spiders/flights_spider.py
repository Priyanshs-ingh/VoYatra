import scrapy
from scrapy import Request
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode
from ..items import FlightItem

class FlightsSpider(scrapy.Spider):
    name = 'flights_spider'
    allowed_domains = [
        'expedia.com', 
        'kayak.com', 
        'skyscanner.com',
        'makemytrip.com',
        'goibibo.com'
    ]
    
    # Custom settings for this spider
    custom_settings = {
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'PLAYWRIGHT_ENABLED': True,
    }
    
    def __init__(self, origin=None, destination=None, departure_date=None, return_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Parse user input parameters
        self.origin = origin or 'DEL'  # Default Delhi
        self.destination = destination or 'BOM'  # Default Mumbai  
        self.departure_date = departure_date or self._get_tomorrow_date()
        self.return_date = return_date  # Optional for round trip
        
        # Airport code mapping for better user experience
        self.airport_codes = {
            # Major Indian cities
            'delhi': 'DEL', 'mumbai': 'BOM', 'bangalore': 'BLR', 'bengaluru': 'BLR',
            'chennai': 'MAA', 'kolkata': 'CCU', 'hyderabad': 'HYD', 'pune': 'PNQ',
            'ahmedabad': 'AMD', 'kochi': 'COK', 'goa': 'GOI', 'jaipur': 'JAI',
            'lucknow': 'LKO', 'bhubaneswar': 'BBI', 'chandigarh': 'IXC',
            'coimbatore': 'CJB', 'indore': 'IDR', 'nagpur': 'NAG',
            'thiruvananthapuram': 'TRV', 'vijayawada': 'VGA', 'vishakhapatnam': 'VTZ',
            
            # International cities
            'london': 'LHR', 'newyork': 'JFK', 'dubai': 'DXB', 'singapore': 'SIN',
            'bangkok': 'BKK', 'kualalumpur': 'KUL', 'doha': 'DOH', 'amsterdam': 'AMS',
            'paris': 'CDG', 'frankfurt': 'FRA', 'toronto': 'YYZ', 'sydney': 'SYD'
        }
        
        # Convert city names to airport codes if needed
        self.origin = self._get_airport_code(self.origin.lower())
        self.destination = self._get_airport_code(self.destination.lower())
        
        # Validate date format
        self.departure_date = self._validate_date(self.departure_date)
        if self.return_date:
            self.return_date = self._validate_date(self.return_date)
            
        self.logger.info(f"🛫 Searching flights: {self.origin} → {self.destination} on {self.departure_date}")
        if self.return_date:
            self.logger.info(f"🛬 Return flight: {self.destination} → {self.origin} on {self.return_date}")
    
    def _get_airport_code(self, city_name):
        """Convert city name to airport code"""
        city_clean = city_name.replace(' ', '').lower()
        return self.airport_codes.get(city_clean, city_name.upper())
    
    def _get_tomorrow_date(self):
        """Get tomorrow's date as default"""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')
    
    def _validate_date(self, date_str):
        """Validate and format date string"""
        try:
            # Try to parse the date in different formats
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d'):
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return tomorrow's date
            self.logger.warning(f"Invalid date format: {date_str}. Using tomorrow's date.")
            return self._get_tomorrow_date()
            
        except Exception as e:
            self.logger.error(f"Date validation error: {e}")
            return self._get_tomorrow_date()
    
    def start_requests(self):
        """Generate requests based on user input"""
        self.logger.info(f"🔍 Generating requests for {self.origin} → {self.destination}")
        
        # Generate requests for each website with user parameters
        yield from self.generate_expedia_requests()
        yield from self.generate_kayak_requests()
        yield from self.generate_skyscanner_requests()
        yield from self.generate_makemytrip_requests()
        yield from self.generate_goibibo_requests()
    
    def generate_expedia_requests(self):
        """Generate Expedia flight search URLs with user input"""
        trip_type = 'roundtrip' if self.return_date else 'oneway'
        
        if self.return_date:
            leg_param = f"from:{self.origin},to:{self.destination},departure:{self.departure_date},return:{self.return_date}"
        else:
            leg_param = f"from:{self.origin},to:{self.destination},departure:{self.departure_date}"
        
        params = {
            'flight-type': 'on',
            'mode': 's',
            'trip': trip_type,
            'leg1': leg_param,
            'passengers': 'children:0,adults:1,seniors:0,infantinlap:Y',
            'options': 'cabinclass:coach',
        }
        
        base_url = 'https://www.expedia.com/Flights-Search'
        url = f"{base_url}?{urlencode(params)}"
        
        self.logger.info(f"📍 Expedia URL: {url}")
        
        yield Request(
            url=url,
            callback=self.parse_expedia,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [5000]},
                ],
                'source': 'expedia'
            }
        )
    
    def generate_kayak_requests(self):
        """Generate Kayak flight search URLs with user input"""
        if self.return_date:
            url = f"https://www.kayak.com/flights/{self.origin}-{self.destination}/{self.departure_date}/{self.return_date}"
        else:
            url = f"https://www.kayak.com/flights/{self.origin}-{self.destination}/{self.departure_date}"
        
        self.logger.info(f"📍 Kayak URL: {url}")
        
        yield Request(
            url=url,
            callback=self.parse_kayak,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [8000]},
                ],
                'source': 'kayak'
            }
        )
    
    def generate_skyscanner_requests(self):
        """Generate Skyscanner flight search URLs with user input"""
        if self.return_date:
            url = f"https://www.skyscanner.com/transport/flights/{self.origin.lower()}/{self.destination.lower()}/{self.departure_date}/{self.return_date}/"
        else:
            url = f"https://www.skyscanner.com/transport/flights/{self.origin.lower()}/{self.destination.lower()}/{self.departure_date}/"
        
        self.logger.info(f"📍 Skyscanner URL: {url}")
        
        yield Request(
            url=url,
            callback=self.parse_skyscanner,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [10000]},
                ],
                'source': 'skyscanner'
            }
        )
    
    def generate_makemytrip_requests(self):
        """Generate MakeMyTrip flight search URLs with user input"""
        # Convert date format for MMT (DDMMYYYY)
        date_obj = datetime.strptime(self.departure_date, '%Y-%m-%d')
        mmt_date = date_obj.strftime('%d%m%Y')
        
        if self.return_date:
            return_date_obj = datetime.strptime(self.return_date, '%Y-%m-%d')
            mmt_return_date = return_date_obj.strftime('%d%m%Y')
            trip_type = 'R'
            itinerary = f"{self.origin}-{self.destination}-{mmt_date}_{self.destination}-{self.origin}-{mmt_return_date}"
        else:
            trip_type = 'O'
            itinerary = f"{self.origin}-{self.destination}-{mmt_date}"
        
        url = f"https://www.makemytrip.com/flight/search?tripType={trip_type}&itinerary={itinerary}&paxType=A-1_C-0_I-0&intl=false&cabinClass=E"
        
        self.logger.info(f"📍 MakeMyTrip URL: {url}")
        
        yield Request(
            url=url,
            callback=self.parse_makemytrip,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [12000]},
                ],
                'source': 'makemytrip'
            }
        )
    
    def generate_goibibo_requests(self):
        """Generate Goibibo flight search URLs with user input"""
        # Convert date format for Goibibo (YYYYMMDD)
        date_obj = datetime.strptime(self.departure_date, '%Y-%m-%d')
        goibibo_date = date_obj.strftime('%Y%m%d')
        
        if self.return_date:
            return_date_obj = datetime.strptime(self.return_date, '%Y-%m-%d')
            goibibo_return_date = return_date_obj.strftime('%Y%m%d')
            url = f"https://www.goibibo.com/flights/{self.origin}-{self.destination}-air-tickets-{goibibo_date}/?return={goibibo_return_date}"
        else:
            url = f"https://www.goibibo.com/flights/{self.origin}-{self.destination}-air-tickets-{goibibo_date}/"
        
        self.logger.info(f"📍 Goibibo URL: {url}")
        
        yield Request(
            url=url,
            callback=self.parse_goibibo,
            meta={
                'playwright': True,
                'playwright_page_methods': [
                    {'method': 'wait_for_load_state', 'args': ['networkidle']},
                    {'method': 'wait_for_timeout', 'args': [8000]},
                ],
                'source': 'goibibo'
            }
        )
    
    def parse_expedia(self, response):
        """Parse Expedia flight results"""
        source = response.meta['source']
        
        # Expedia flight result selectors
        flights = response.css('div[data-test-id="offer-listing"]')
        
        for flight in flights:
            try:
                # Extract flight information
                airline = flight.css('.airline-name ::text').get()
                price_text = flight.css('[data-test-id="listing-price-dollars"] ::text').get()
                duration = flight.css('.duration-emphasis ::text').get()
                departure_time = flight.css('.departure-time ::text').get()
                arrival_time = flight.css('.arrival-time ::text').get()
                stops = flight.css('.stops-text ::text').get() or '0'
                
                # Clean price
                price = self.extract_price(price_text) if price_text else None
                
                if price and airline:
                    item = FlightItem()
                    item['origin'] = self.origin
                    item['destination'] = self.destination
                    item['departure_date'] = self.departure_date
                    item['return_date'] = self.return_date
                    item['airline'] = airline.strip()
                    item['price'] = price
                    item['currency'] = 'USD'
                    item['duration'] = duration.strip() if duration else None
                    item['stops'] = self.parse_stops(stops)
                    item['departure_time'] = departure_time.strip() if departure_time else None
                    item['arrival_time'] = arrival_time.strip() if arrival_time else None
                    item['source_url'] = response.url
                    item['scraped_at'] = datetime.now().isoformat()
                    item['data_type'] = 'flights'
                    
                    yield item
                    
            except Exception as e:
                self.logger.error(f"Error parsing Expedia flight: {e}")
                continue
    
    def parse_kayak(self, response):
        """Parse Kayak flight results"""
        # Kayak flight result selectors
        flights = response.css('.nrc6, .Hv20, [data-resultid]')
        
        for flight in flights:
            try:
                airline = flight.css('.c_cgF .c5iUd ::text').get()
                price_text = flight.css('.price-text, .f8F1-price-text ::text').get()
                duration = flight.css('.vmXl .vmXl-mod-variant-default ::text').get()
                stops_element = flight.css('.JWEO .JWEO-stops-text ::text').get()
                departure_time = flight.css('.depart-time ::text').get()
                arrival_time = flight.css('.arrival-time ::text').get()
                
                price = self.extract_price(price_text) if price_text else None
                
                if price and airline:
                    item = FlightItem()
                    item['origin'] = self.origin
                    item['destination'] = self.destination
                    item['departure_date'] = self.departure_date
                    item['return_date'] = self.return_date
                    item['airline'] = airline.strip()
                    item['price'] = price
                    item['currency'] = 'USD'
                    item['duration'] = duration.strip() if duration else None
                    item['stops'] = self.parse_stops(stops_element) if stops_element else 0
                    item['departure_time'] = departure_time.strip() if departure_time else None
                    item['arrival_time'] = arrival_time.strip() if arrival_time else None
                    item['source_url'] = response.url
                    item['scraped_at'] = datetime.now().isoformat()
                    item['data_type'] = 'flights'
                    
                    yield item
                    
            except Exception as e:
                self.logger.error(f"Error parsing Kayak flight: {e}")
                continue
    
    def parse_skyscanner(self, response):
        """Parse Skyscanner flight results"""
        # Try JSON data first
        script_data = response.css('script:contains("window.INITIAL_STATE")::text').get()
        
        if script_data:
            try:
                json_start = script_data.find('{"query":')
                json_end = script_data.find(';</script>')
                
                if json_start > -1 and json_end > -1:
                    json_data = script_data[json_start:json_end]
                    data = json.loads(json_data)
                    
                    if 'results' in data and 'itineraries' in data['results']:
                        for itinerary in data['results']['itineraries'].values():
                            try:
                                price_raw = itinerary.get('price', {}).get('raw')
                                airline_id = itinerary.get('legs', [{}])[0].get('carriers', [{}])[0].get('alternativeId', '')
                                duration = itinerary.get('legs', [{}])[0].get('durationInMinutes', 0)
                                stops = len(itinerary.get('legs', [{}])[0].get('stops', [])) 
                                
                                if price_raw:
                                    item = FlightItem()
                                    item['origin'] = self.origin
                                    item['destination'] = self.destination
                                    item['departure_date'] = self.departure_date
                                    item['return_date'] = self.return_date
                                    item['airline'] = airline_id
                                    item['price'] = float(price_raw)
                                    item['currency'] = 'USD'
                                    item['duration'] = f"{duration // 60}h {duration % 60}m" if duration else None
                                    item['stops'] = stops
                                    item['source_url'] = response.url
                                    item['scraped_at'] = datetime.now().isoformat()
                                    item['data_type'] = 'flights'
                                    
                                    yield item
                                    
                            except Exception as e:
                                continue
                                
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing Skyscanner JSON: {e}")
        
        # Fallback to CSS selectors
        flights = response.css('[data-testid="result"]')
        for flight in flights[:5]:
            try:
                price_text = flight.css('[data-testid="price"] ::text').get()
                airline = flight.css('[data-testid="carrier-logo"] ::attr(alt)').get()
                duration = flight.css('[data-testid="duration"] ::text').get()
                
                price = self.extract_price(price_text) if price_text else None
                
                if price and airline:
                    item = FlightItem()
                    item['origin'] = self.origin
                    item['destination'] = self.destination
                    item['departure_date'] = self.departure_date
                    item['return_date'] = self.return_date
                    item['airline'] = airline.strip()
                    item['price'] = price
                    item['currency'] = 'USD'
                    item['duration'] = duration.strip() if duration else None
                    item['stops'] = 0
                    item['source_url'] = response.url
                    item['scraped_at'] = datetime.now().isoformat()
                    item['data_type'] = 'flights'
                    
                    yield item
                    
            except Exception as e:
                continue
    
    def parse_makemytrip(self, response):
        """Parse MakeMyTrip flight results"""
        flights = response.css('.listingCard, .flightCard')
        
        for flight in flights:
            try:
                airline = flight.css('.carrierName, .airline-name ::text').get()
                price_text = flight.css('.actualPrice, .price ::text').get()
                duration = flight.css('.duration-info, .flightDuration ::text').get()
                stops = flight.css('.stop-info, .stopInfo ::text').get()
                departure_time = flight.css('.dept-time ::text').get()
                arrival_time = flight.css('.arrival-time ::text').get()
                
                price = self.extract_price(price_text, currency_symbol='₹') if price_text else None
                
                if price and airline:
                    item = FlightItem()
                    item['origin'] = self.origin
                    item['destination'] = self.destination
                    item['departure_date'] = self.departure_date
                    item['return_date'] = self.return_date
                    item['airline'] = airline.strip()
                    item['price'] = price
                    item['currency'] = 'INR'
                    item['duration'] = duration.strip() if duration else None
                    item['stops'] = self.parse_stops(stops) if stops else 0
                    item['departure_time'] = departure_time.strip() if departure_time else None
                    item['arrival_time'] = arrival_time.strip() if arrival_time else None
                    item['source_url'] = response.url
                    item['scraped_at'] = datetime.now().isoformat()
                    item['data_type'] = 'flights'
                    
                    yield item
                    
            except Exception as e:
                continue
    
    def parse_goibibo(self, response):
        """Parse Goibibo flight results"""
        flights = response.css('.flightCardWrap, .flight-card')
        
        for flight in flights:
            try:
                airline = flight.css('.airlineName, .airline ::text').get()
                price_text = flight.css('.priceNew, .price-info ::text').get()
                duration = flight.css('.durationInfo ::text').get()
                stops = flight.css('.stopInfo ::text').get()
                departure_time = flight.css('.dept-time ::text').get()
                arrival_time = flight.css('.arrival-time ::text').get()
                
                price = self.extract_price(price_text, currency_symbol='₹') if price_text else None
                
                if price and airline:
                    item = FlightItem()
                    item['origin'] = self.origin
                    item['destination'] = self.destination
                    item['departure_date'] = self.departure_date
                    item['return_date'] = self.return_date
                    item['airline'] = airline.strip()
                    item['price'] = price
                    item['currency'] = 'INR'
                    item['duration'] = duration.strip() if duration else None
                    item['stops'] = self.parse_stops(stops) if stops else 0
                    item['departure_time'] = departure_time.strip() if departure_time else None
                    item['arrival_time'] = arrival_time.strip() if arrival_time else None
                    item['source_url'] = response.url
                    item['scraped_at'] = datetime.now().isoformat()
                    item['data_type'] = 'flights'
                    
                    yield item
                    
            except Exception as e:
                continue
    
    def extract_price(self, price_text, currency_symbol='$'):
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        try:
            # Remove currency symbols and commas
            price_clean = price_text.replace(currency_symbol, '').replace(',', '').replace(' ', '')
            # Extract numbers using regex
            import re
            price_match = re.search(r'[\d.]+', price_clean)
            if price_match:
                return float(price_match.group())
        except:
            pass
        
        return None
    
    def parse_stops(self, stops_text):
        """Parse stops information"""
        if not stops_text:
            return 0
        
        stops_text = stops_text.lower()
        if 'non-stop' in stops_text or 'nonstop' in stops_text or 'direct' in stops_text:
            return 0
        elif '1 stop' in stops_text:
            return 1
        elif '2 stop' in stops_text:
            return 2
        else:
            # Try to extract number
            import re
            match = re.search(r'(\d+)', stops_text)
            if match:
                return int(match.group(1))
        
        return 0