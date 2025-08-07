"""
Self-Sufficient Flight Scraper - No External APIs Required
This spider uses advanced techniques to bypass anti-bot measures independently
"""

import scrapy
import json
import random
import time
import re
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
from ..items import FlightItem

class SelfSufficientFlightSpider(scrapy.Spider):
    name = 'flights_spider_self_sufficient'
    
    # Dynamic allowed domains - will be updated based on successful responses
    allowed_domains = []
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0,  # We'll handle delays manually
        'RANDOMIZE_DOWNLOAD_DELAY': 0,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS': 2,
        'PLAYWRIGHT_ENABLED': True,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ]
        },
        'ROBOTSTXT_OBEY': False,  # We'll be respectful but not bound by robots.txt
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    def __init__(self, origin=None, destination=None, departure_date=None, return_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # User input processing
        self.origin = self._convert_to_airport_code(origin or 'DEL')
        self.destination = self._convert_to_airport_code(destination or 'BOM')
        self.departure_date = self._parse_date(departure_date) or self._get_tomorrow_date()
        self.return_date = self._parse_date(return_date) if return_date else None
        
        # Airport code mapping
        self.airport_codes = {
            'delhi': 'DEL', 'mumbai': 'BOM', 'bangalore': 'BLR', 'bengaluru': 'BLR',
            'chennai': 'MAA', 'kolkata': 'CCU', 'hyderabad': 'HYD', 'pune': 'PNQ',
            'ahmedabad': 'AMD', 'kochi': 'COK', 'goa': 'GOI', 'jaipur': 'JAI',
            'lucknow': 'LKO', 'bhubaneswar': 'BBI', 'chandigarh': 'IXC',
            'coimbatore': 'CJB', 'indore': 'IDR', 'nagpur': 'NAG'
        }
        
        # Anti-detection arsenal
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Alternative data sources - less protected endpoints
        self.alternative_sources = [
            'airport_websites',
            'airline_mobile_apis',
            'travel_forums',
            'cached_data_sources'
        ]
        
        self.logger.info(f"🛫 Self-sufficient search: {self.origin} → {self.destination} on {self.departure_date}")
    
    def _convert_to_airport_code(self, location):
        """Convert city name to airport code"""
        if not location:
            return 'DEL'
        location_lower = location.lower().strip()
        return self.airport_codes.get(location_lower, location.upper())
    
    def _parse_date(self, date_str):
        """Parse various date formats"""
        if not date_str:
            return None
            
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None
    
    def _get_tomorrow_date(self):
        """Get tomorrow's date"""
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    def start_requests(self):
        """Generate requests using multiple strategies"""
        
        # Strategy 1: Direct airline websites (less protected)
        yield from self._generate_airline_direct_requests()
        
        # Strategy 2: Alternative flight data sources
        yield from self._generate_alternative_source_requests()
        
        # Strategy 3: Mobile endpoints (often less protected)
        yield from self._generate_mobile_requests()
        
        # Strategy 4: Cached/Historical data endpoints
        yield from self._generate_cached_data_requests()
    
    def _generate_airline_direct_requests(self):
        """Generate requests to airline websites directly"""
        airlines = [
            {
                'name': 'Air India',
                'url_template': 'https://www.airindia.in/in/en/book/flight-search.html',
                'params': {
                    'from': self.origin,
                    'to': self.destination,
                    'departure': self.departure_date,
                    'return': self.return_date or '',
                    'adult': '1',
                    'child': '0',
                    'infant': '0'
                }
            },
            {
                'name': 'SpiceJet',
                'url_template': 'https://book.spicejet.com/SearchFlights.aspx',
                'params': {
                    'o': self.origin,
                    'd': self.destination,
                    'dd': self.departure_date,
                    'rd': self.return_date or '',
                    'a': '1',
                    'c': '0',
                    'i': '0'
                }
            },
            {
                'name': 'IndiGo',
                'url_template': 'https://www.goindigo.in/flight-booking',
                'params': {
                    'origin': self.origin,
                    'destination': self.destination,
                    'departDate': self.departure_date
                }
            }
        ]
        
        for airline in airlines:
            url = f"{airline['url_template']}?{urlencode(airline['params'])}"
            
            yield scrapy.Request(
                url=url,
                callback=self.parse_airline_direct,
                headers={
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Referer': airline['url_template'].split('/')[2]
                },
                meta={
                    'airline': airline['name'],
                    'playwright': True,
                    'playwright_page_methods': [
                        {'method': 'wait_for_load_state', 'args': ['networkidle']},
                        {'method': 'wait_for_timeout', 'args': [random.randint(3000, 7000)]},
                    ]
                },
                dont_filter=True
            )
            
            # Add random delay between requests
            time.sleep(random.uniform(2, 5))
    
    def _generate_alternative_source_requests(self):
        """Generate requests to alternative, less-protected sources"""
        
        # Airport departure/arrival boards (public data)
        airport_urls = [
            f"https://www.flightradar24.com/airport/{self.origin.lower()}",
            f"https://www.flightradar24.com/airport/{self.destination.lower()}"
        ]
        
        for url in airport_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_flight_tracker,
                headers={'User-Agent': random.choice(self.user_agents)},
                meta={'source': 'flight_tracker'},
                dont_filter=True
            )
    
    def _generate_mobile_requests(self):
        """Generate mobile API requests (often less protected)"""
        
        # Mobile user agents are often less blocked
        mobile_user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/118.0 Firefox/118.0'
        ]
        
        # Try mobile versions of travel sites
        mobile_sites = [
            f"https://m.makemytrip.com/flight/search?from={self.origin}&to={self.destination}&date={self.departure_date}",
            f"https://m.goibibo.com/flights/?from={self.origin}&to={self.destination}&date={self.departure_date}"
        ]
        
        for url in mobile_sites:
            yield scrapy.Request(
                url=url,
                callback=self.parse_mobile_results,
                headers={
                    'User-Agent': random.choice(mobile_user_agents),
                    'Accept': 'application/json, text/plain, */*'
                },
                meta={'source': 'mobile'},
                dont_filter=True
            )
    
    def _generate_cached_data_requests(self):
        """Generate requests for cached/historical data"""
        
        # Many sites have API endpoints that return JSON data
        api_endpoints = [
            # These are examples - real endpoints would be discovered through analysis
            f"https://www.example-travel-site.com/api/flights?origin={self.origin}&dest={self.destination}",
            f"https://www.another-site.com/search/api?from={self.origin}&to={self.destination}"
        ]
        
        for url in api_endpoints:
            yield scrapy.Request(
                url=url,
                callback=self.parse_api_response,
                headers={
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                meta={'source': 'api'},
                dont_filter=True
            )
    
    async def parse_airline_direct(self, response):
        """Parse airline direct booking pages"""
        airline = response.meta.get('airline', 'Unknown')
        page = response.meta.get('playwright_page')
        
        self.logger.info(f"Parsing {airline} - Status: {response.status}")
        
        if page:
            try:
                # Wait for flight results to load
                await page.wait_for_timeout(5000)
                
                # Look for common flight result patterns
                flights_data = await page.evaluate('''
                    () => {
                        const flights = [];
                        
                        // Common selectors for flight cards
                        const selectors = [
                            '.flight-card', '.flight-result', '.search-result',
                            '.flight-item', '.booking-option', '.fare-option'
                        ];
                        
                        for (const selector of selectors) {
                            const elements = document.querySelectorAll(selector);
                            if (elements.length > 0) {
                                elements.forEach((el, idx) => {
                                    if (idx < 5) { // Limit to first 5 results
                                        try {
                                            const priceEl = el.querySelector('[class*="price"], [class*="fare"], [class*="cost"]');
                                            const timeEl = el.querySelector('[class*="time"], [class*="depart"], [class*="schedule"]');
                                            const airlineEl = el.querySelector('[class*="airline"], [class*="carrier"]');
                                            
                                            if (priceEl && priceEl.textContent.trim()) {
                                                flights.push({
                                                    price: priceEl.textContent.trim(),
                                                    time: timeEl ? timeEl.textContent.trim() : '',
                                                    airline: airlineEl ? airlineEl.textContent.trim() : '',
                                                    selector_used: selector
                                                });
                                            }
                                        } catch (e) {
                                            console.log('Error parsing element:', e);
                                        }
                                    }
                                });
                                break; // Stop after finding results with first working selector
                            }
                        }
                        
                        return flights;
                    }
                ''')
                
                # Process found flights
                for flight_data in flights_data:
                    item = self._create_flight_item(
                        airline=flight_data.get('airline', airline),
                        price=flight_data.get('price', ''),
                        time_info=flight_data.get('time', ''),
                        source=f"{airline} Direct",
                        url=response.url
                    )
                    if item:
                        yield item
                
                self.logger.info(f"Found {len(flights_data)} flights from {airline}")
                
            except Exception as e:
                self.logger.error(f"Error parsing {airline}: {str(e)}")
            finally:
                await page.close()
    
    def parse_flight_tracker(self, response):
        """Parse flight tracking websites for real flight data"""
        try:
            # Extract flight information from tracking sites
            flights = response.css('.flight-row, .departure-row, .arrival-row')
            
            for flight in flights[:5]:
                airline = flight.css('.airline ::text').get()
                flight_number = flight.css('.flight-number ::text').get()
                time = flight.css('.time ::text').get()
                
                if airline and flight_number:
                    # Create a basic flight item from real flight data
                    item = self._create_flight_item(
                        airline=airline.strip(),
                        flight_number=flight_number.strip(),
                        time_info=time.strip() if time else '',
                        source='Flight Tracker',
                        url=response.url
                    )
                    if item:
                        yield item
                        
        except Exception as e:
            self.logger.error(f"Error parsing flight tracker: {str(e)}")
    
    def parse_mobile_results(self, response):
        """Parse mobile site results"""
        try:
            # Try to parse JSON response first
            if response.headers.get('content-type', '').startswith('application/json'):
                data = json.loads(response.text)
                # Process JSON flight data
                if isinstance(data, dict) and 'flights' in data:
                    for flight in data['flights'][:5]:
                        item = self._create_flight_item(
                            airline=flight.get('airline', ''),
                            price=flight.get('price', ''),
                            time_info=flight.get('departure_time', ''),
                            source='Mobile API',
                            url=response.url
                        )
                        if item:
                            yield item
            else:
                # Parse HTML response
                flights = response.css('.flight, .result, .card')
                for flight in flights[:5]:
                    price = flight.css('[class*="price"] ::text').get()
                    airline = flight.css('[class*="airline"] ::text').get()
                    time = flight.css('[class*="time"] ::text').get()
                    
                    if price and airline:
                        item = self._create_flight_item(
                            airline=airline.strip(),
                            price=price.strip(),
                            time_info=time.strip() if time else '',
                            source='Mobile Site',
                            url=response.url
                        )
                        if item:
                            yield item
                            
        except Exception as e:
            self.logger.error(f"Error parsing mobile results: {str(e)}")
    
    def parse_api_response(self, response):
        """Parse API responses"""
        try:
            if response.headers.get('content-type', '').startswith('application/json'):
                data = json.loads(response.text)
                # Process API flight data based on common API response patterns
                # This would be customized based on actual API responses discovered
                pass
        except Exception as e:
            self.logger.error(f"Error parsing API response: {str(e)}")
    
    def _create_flight_item(self, airline, price, time_info, source, url, flight_number=''):
        """Create a standardized flight item"""
        try:
            # Clean and validate data
            cleaned_price = self._extract_price(price)
            if not cleaned_price or not airline.strip():
                return None
            
            item = FlightItem()
            item['origin'] = self.origin
            item['destination'] = self.destination
            item['departure_date'] = self.departure_date
            item['return_date'] = self.return_date
            item['airline'] = airline.strip()
            item['price'] = cleaned_price
            item['currency'] = self._detect_currency(price)
            item['flight_number'] = flight_number
            item['departure_time'] = self._extract_time(time_info)
            item['source_url'] = url
            item['source'] = source
            item['scraped_at'] = datetime.now().isoformat()
            item['data_type'] = 'flights'
            
            return item
            
        except Exception as e:
            self.logger.error(f"Error creating flight item: {str(e)}")
            return None
    
    def _extract_price(self, price_text):
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        try:
            # Remove common currency symbols and clean the text
            price_clean = re.sub(r'[₹$€£¥,\s]', '', str(price_text))
            # Extract numbers
            price_match = re.search(r'\d+\.?\d*', price_clean)
            if price_match:
                return float(price_match.group())
        except:
            pass
        
        return None
    
    def _detect_currency(self, price_text):
        """Detect currency from price text"""
        if not price_text:
            return 'INR'
        
        if '₹' in price_text:
            return 'INR'
        elif '$' in price_text:
            return 'USD'
        elif '€' in price_text:
            return 'EUR'
        elif '£' in price_text:
            return 'GBP'
        else:
            return 'INR'  # Default for Indian routes
    
    def _extract_time(self, time_text):
        """Extract time information"""
        if not time_text:
            return None
        
        # Look for time patterns like "14:30", "2:30 PM", etc.
        time_pattern = r'\d{1,2}:\d{2}(?:\s*[APap][Mm])?'
        time_match = re.search(time_pattern, str(time_text))
        if time_match:
            return time_match.group()
        
        return time_text.strip()[:10]  # Fallback to first 10 characters
