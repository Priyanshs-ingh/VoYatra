import scrapy
from scrapy import Request
import json
import re
import random
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode
from ..items import FlightItem

class FlightsSpiderEnhanced(scrapy.Spider):
    name = 'flights_spider_enhanced'
    
    # Custom settings with anti-detection measures
    custom_settings = {
        'DOWNLOAD_DELAY': random.uniform(3, 7),  # Random delays
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,  # Be more conservative
        'PLAYWRIGHT_ENABLED': True,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,  # Set to False for debugging
            'args': [
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        },
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,  # 60 seconds
        'PLAYWRIGHT_PAGE_METHODS': [
            'wait_for_timeout',  # Wait for page to load
            'wait_for_selector',  # Wait for specific elements
        ]
    }
    
    def __init__(self, origin=None, destination=None, departure_date=None, return_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Parse user input parameters
        self.origin = self._convert_to_airport_code(origin or 'DEL')
        self.destination = self._convert_to_airport_code(destination or 'BOM')
        self.departure_date = self._parse_date(departure_date) or self._get_tomorrow_date()
        self.return_date = self._parse_date(return_date) if return_date else None
        
        # Airport code mapping
        self.airport_codes = {
            'delhi': 'DEL', 'mumbai': 'BOM', 'bangalore': 'BLR', 'bengaluru': 'BLR',
            'chennai': 'MAA', 'kolkata': 'CCU', 'hyderabad': 'HYD', 'pune': 'PNQ',
            'ahmedabad': 'AMD', 'kochi': 'COK', 'goa': 'GOI', 'jaipur': 'JAI',
            'lucknow': 'LKO', 'bhubaneswar': 'BBI', 'chandigarh': 'IXC'
        }
        
        # User agents pool for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
        ]
        
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
        """Generate requests for different flight booking sites with anti-detection"""
        
        # Start with more reliable APIs and aggregators
        sites_config = [
            {
                'name': 'MakeMyTrip',
                'url_template': self._generate_makemytrip_url(),
                'priority': 1,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Cache-Control': 'no-cache',
                    'Upgrade-Insecure-Requests': '1'
                }
            },
            {
                'name': 'Goibibo',
                'url_template': self._generate_goibibo_url(),
                'priority': 2,
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8',
                    'Referer': 'https://www.goibibo.com/'
                }
            }
        ]
        
        # Generate requests with random delays and headers
        for site in sites_config:
            headers = site['headers'].copy()
            headers['User-Agent'] = random.choice(self.user_agents)
            
            yield Request(
                url=site['url_template'],
                callback=self.parse_flight_results,
                headers=headers,
                priority=site['priority'],
                meta={
                    'site_name': site['name'],
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        'wait_for_load_state',
                        'wait_for_timeout'
                    ]
                },
                dont_filter=True
            )
            
            # Add random delay between requests
            time.sleep(random.uniform(2, 5))
    
    def _generate_makemytrip_url(self):
        """Generate MakeMyTrip search URL"""
        params = {
            'from': self.origin,
            'to': self.destination,
            'departure': self.departure_date,
            'adults': '1',
            'children': '0',
            'infants': '0',
            'class': 'E'  # Economy
        }
        
        if self.return_date:
            params['return'] = self.return_date
            trip_type = 'R'  # Round trip
        else:
            trip_type = 'O'  # One way
            
        base_url = f"https://www.makemytrip.com/flight/search?tripType={trip_type}&"
        return base_url + urlencode(params)
    
    def _generate_goibibo_url(self):
        """Generate Goibibo search URL"""
        params = {
            'from': self.origin,
            'to': self.destination,
            'dateDeparture': self.departure_date,
            'adults': '1',
            'children': '0',
            'infants': '0'
        }
        
        if self.return_date:
            params['dateArrival'] = self.return_date
            
        base_url = "https://www.goibibo.com/flights/"
        return base_url + f"{self.origin}-{self.destination}-" + urlencode(params, safe='-')
    
    async def parse_flight_results(self, response):
        """Parse flight search results with enhanced extraction"""
        site_name = response.meta.get('site_name', 'Unknown')
        page = response.meta.get('playwright_page')
        
        self.logger.info(f"Parsing {site_name} - Status: {response.status}")
        
        if page:
            # Wait for content to load
            await page.wait_for_timeout(5000)  # Wait 5 seconds
            
            # Try to wait for flight results to load
            try:
                if site_name == 'MakeMyTrip':
                    await self._parse_makemytrip_flights(page, response)
                elif site_name == 'Goibibo':
                    await self._parse_goibibo_flights(page, response)
                    
            except Exception as e:
                self.logger.error(f"Error parsing {site_name}: {str(e)}")
                
        await page.close() if page else None
    
    async def _parse_makemytrip_flights(self, page, response):
        """Parse MakeMyTrip flight results"""
        try:
            # Wait for flight listings to appear
            await page.wait_for_selector('.listingCard', timeout=30000)
            
            # Extract flight data
            flights = await page.evaluate('''
                () => {
                    const flightCards = document.querySelectorAll('.listingCard');
                    const flights = [];
                    
                    flightCards.forEach(card => {
                        try {
                            const airline = card.querySelector('.airline-info')?.textContent?.trim() || '';
                            const price = card.querySelector('.price')?.textContent?.trim() || '';
                            const departure = card.querySelector('.dept-time')?.textContent?.trim() || '';
                            const arrival = card.querySelector('.arrival-time')?.textContent?.trim() || '';
                            const duration = card.querySelector('.duration')?.textContent?.trim() || '';
                            
                            if (airline && price) {
                                flights.push({
                                    airline: airline,
                                    price: price,
                                    departure_time: departure,
                                    arrival_time: arrival,
                                    duration: duration
                                });
                            }
                        } catch (e) {
                            console.log('Error parsing flight card:', e);
                        }
                    });
                    
                    return flights;
                }
            ''')
            
            # Create flight items
            for flight_data in flights:
                item = FlightItem()
                item['source'] = 'MakeMyTrip'
                item['airline'] = flight_data.get('airline', '')
                item['price'] = self._clean_price(flight_data.get('price', ''))
                item['departure_time'] = flight_data.get('departure_time', '')
                item['arrival_time'] = flight_data.get('arrival_time', '')
                item['duration'] = flight_data.get('duration', '')
                item['origin'] = self.origin
                item['destination'] = self.destination
                item['departure_date'] = self.departure_date
                item['data_type'] = 'flights'
                item['scraped_at'] = datetime.now().isoformat()
                
                yield item
                
        except Exception as e:
            self.logger.error(f"MakeMyTrip parsing error: {str(e)}")
            
    async def _parse_goibibo_flights(self, page, response):
        """Parse Goibibo flight results"""
        try:
            # Wait for flight listings
            await page.wait_for_selector('[data-testid="flight-card"]', timeout=30000)
            
            flights = await page.evaluate('''
                () => {
                    const flightCards = document.querySelectorAll('[data-testid="flight-card"]');
                    const flights = [];
                    
                    flightCards.forEach(card => {
                        try {
                            const airline = card.querySelector('.airline-name')?.textContent?.trim() || '';
                            const price = card.querySelector('.price-text')?.textContent?.trim() || '';
                            const departure = card.querySelector('.departure-time')?.textContent?.trim() || '';
                            const arrival = card.querySelector('.arrival-time')?.textContent?.trim() || '';
                            
                            if (airline && price) {
                                flights.push({
                                    airline: airline,
                                    price: price,
                                    departure_time: departure,
                                    arrival_time: arrival
                                });
                            }
                        } catch (e) {
                            console.log('Error parsing Goibibo flight card:', e);
                        }
                    });
                    
                    return flights;
                }
            ''')
            
            for flight_data in flights:
                item = FlightItem()
                item['source'] = 'Goibibo'
                item['airline'] = flight_data.get('airline', '')
                item['price'] = self._clean_price(flight_data.get('price', ''))
                item['departure_time'] = flight_data.get('departure_time', '')
                item['arrival_time'] = flight_data.get('arrival_time', '')
                item['origin'] = self.origin
                item['destination'] = self.destination
                item['departure_date'] = self.departure_date
                item['data_type'] = 'flights'
                item['scraped_at'] = datetime.now().isoformat()
                
                yield item
                
        except Exception as e:
            self.logger.error(f"Goibibo parsing error: {str(e)}")
    
    def _clean_price(self, price_text):
        """Clean and extract price from text"""
        if not price_text:
            return ''
        
        # Extract numbers from price text
        price_numbers = re.findall(r'[\d,]+', price_text.replace('₹', '').replace(',', ''))
        return price_numbers[0] if price_numbers else price_text.strip()
