import scrapy
import json
import re
from urllib.parse import urlencode
from scrapy.http import Request, FormRequest


class BookingSpider(scrapy.Spider):
    name = "booking_spider"
    allowed_domains = ["booking.com"]
    
    # Custom settings for this spider
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'COOKIES_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'travel_scrapers.middlewares.SeleniumMiddleware': 543,
        }
    }

    def __init__(self, destination="Bangalore", checkin="2025-08-15", checkout="2025-08-17", *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        self.destination = destination
        self.checkin = checkin
        self.checkout = checkout
        self.results = []

    def start_requests(self):
        """Generate initial search request"""
        checkin_year, checkin_month, checkin_day = self.checkin.split("-")
        checkout_year, checkout_month, checkout_day = self.checkout.split("-")
        
        search_params = {
            "ss": self.destination,
            "checkin_year": checkin_year,
            "checkin_month": checkin_month,
            "checkin_monthday": checkin_day,
            "checkout_year": checkout_year,
            "checkout_month": checkout_month,
            "checkout_monthday": checkout_day,
            "no_rooms": 1,
            "group_adults": 2,
            "group_children": 0
        }
        
        search_url = "https://www.booking.com/searchresults.en-gb.html?" + urlencode(search_params)
        
        yield Request(
            url=search_url,
            callback=self.parse_search_page,
            meta={'search_params': search_params}
        )

    def parse_search_page(self, response):
        """Parse the search results page"""
        self.logger.info(f"Processing search page: {response.url}")
        
        # Extract hotel data from the page
        hotels = self.extract_hotel_data(response)
        
        for hotel in hotels:
            yield hotel
            
        # Try to extract GraphQL data for additional results
        graphql_body = self.extract_graphql_body(response)
        if graphql_body:
            yield self.make_graphql_request(response, graphql_body, 0)
        
        # Look for pagination and follow next pages
        next_page_url = response.css('a[aria-label="Next page"]::attr(href)').get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse_search_page)

    def extract_hotel_data(self, response):
        """Extract hotel data from the HTML response"""
        hotels = []
        
        # Try multiple selectors for hotel cards
        hotel_selectors = [
            '[data-testid="property-card"]',
            '.sr_property_block',
            '.fcab3ed991.a23c043802',
            '.d20f4628d0'
        ]
        
        hotel_elements = []
        for selector in hotel_selectors:
            elements = response.css(selector)
            if elements:
                hotel_elements = elements
                self.logger.info(f"Found {len(elements)} hotels using selector: {selector}")
                break
        
        for hotel in hotel_elements:
            try:
                hotel_data = {
                    'name': self.extract_text(hotel, [
                        '[data-testid="title"]::text',
                        '.sr-hotel__name::text',
                        '.fcab3ed991::text',
                        'h3 a::text'
                    ]),
                    'location': self.extract_text(hotel, [
                        '[data-testid="address"]::text',
                        '.sr-hotel__address::text',
                        '.f4bd0794db::text'
                    ]),
                    'rating': self.extract_text(hotel, [
                        '[data-testid="review-score"]::text',
                        '.bui-review-score__badge::text',
                        '.a3b8729ab1::text'
                    ]),
                    'price': self.extract_text(hotel, [
                        '[data-testid="price-and-discounted-price"]::text',
                        '.bui-price-display__value::text',
                        '.fcab3ed991.bd73d13072::text'
                    ]),
                    'url': self.extract_text(hotel, [
                        'h3 a::attr(href)',
                        '.hotel_name_link::attr(href)',
                        'a::attr(href)'
                    ]),
                    'image_url': self.extract_text(hotel, [
                        'img::attr(src)',
                        '.hotel_image::attr(src)'
                    ]),
                    'reviews_count': self.extract_text(hotel, [
                        '[data-testid="review-score-right-component"]::text',
                        '.bui-review-score__text::text'
                    ])
                }
                
                # Clean and validate data
                if hotel_data['name']:
                    hotels.append(self.clean_hotel_data(hotel_data))
                    
            except Exception as e:
                self.logger.error(f"Error extracting hotel data: {e}")
                continue
        
        return hotels

    def extract_text(self, element, selectors):
        """Try multiple selectors and return first match"""
        for selector in selectors:
            result = element.css(selector).get()
            if result and result.strip():
                return result.strip()
        return None

    def clean_hotel_data(self, hotel_data):
        """Clean and format hotel data"""
        # Clean price
        if hotel_data.get('price'):
            price_match = re.search(r'[\d,]+', hotel_data['price'].replace(',', ''))
            hotel_data['price_numeric'] = int(price_match.group()) if price_match else None
        
        # Clean rating
        if hotel_data.get('rating'):
            rating_match = re.search(r'\d+\.?\d*', hotel_data['rating'])
            hotel_data['rating_numeric'] = float(rating_match.group()) if rating_match else None
        
        # Clean reviews count
        if hotel_data.get('reviews_count'):
            reviews_match = re.search(r'[\d,]+', hotel_data['reviews_count'].replace(',', ''))
            hotel_data['reviews_count_numeric'] = int(reviews_match.group()) if reviews_match else None
        
        # Make URL absolute
        if hotel_data.get('url') and not hotel_data['url'].startswith('http'):
            hotel_data['url'] = 'https://www.booking.com' + hotel_data['url']
            
        return hotel_data

    def extract_graphql_body(self, response):
        """Extract GraphQL request body from Apollo cache"""
        try:
            # Look for Apollo cache data
            apollo_script = response.xpath('//script[@data-capla-store-data="apollo"]/text()').get()
            if not apollo_script:
                self.logger.warning("No Apollo GraphQL data found")
                return None
                
            apollo_data = json.loads(apollo_script)
            
            if "ROOT_QUERY" not in apollo_data:
                return None
                
            search_queries = apollo_data["ROOT_QUERY"].get("searchQueries", {})
            search_keys = [key for key in search_queries.keys() if key.startswith("search(")]
            
            if len(search_keys) < 1:
                return None
                
            # Use the first search key
            search_key = search_keys[0]
            search_params_str = search_key[len("search("):-1]
            search_params = json.loads(search_params_str)
            
            # Build GraphQL query
            graphql_body = {
                "operationName": "FullSearch",
                "variables": {
                    "input": search_params["input"]
                },
                "extensions": {},
                "query": """
                query FullSearch($input: SearchQueryInput!) {
                  searchQueries {
                    search(input: $input) {
                      results {
                        __typename
                        ... on SearchResultProperty {
                          basicPropertyData {
                            id
                            name
                            location {
                              displayLocation
                            }
                            reviewScore {
                              score
                              totalScoreCount
                            }
                            pageName
                            photos {
                              main {
                                highResUrl {
                                  absoluteUrl
                                }
                              }
                            }
                          }
                          priceDisplayInfoIrene {
                            displayPrice {
                              amount
                              currency
                            }
                            totalPrice {
                              amount
                              currency
                            }
                          }
                          blocks {
                            finalPrice {
                              amount
                              currency
                            }
                          }
                        }
                      }
                      totalCount
                    }
                  }
                }
                """
            }
            
            return graphql_body
            
        except Exception as e:
            self.logger.error(f"Error extracting GraphQL body: {e}")
            return None

    def make_graphql_request(self, response, graphql_body, offset=0):
        """Make GraphQL API request"""
        # Add pagination offset
        if "pagination" not in graphql_body["variables"]["input"]:
            graphql_body["variables"]["input"]["pagination"] = {}
        graphql_body["variables"]["input"]["pagination"]["offset"] = offset
        
        # Extract URL parameters from the original search
        url_params = response.url.split('?')[1] if '?' in response.url else ''
        
        graphql_url = f"https://www.booking.com/dml/graphql?{url_params}"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://www.booking.com',
            'Referer': response.url,
            'User-Agent': response.request.headers.get('User-Agent', '').decode(),
        }
        
        return FormRequest(
            url=graphql_url,
            method='POST',
            headers=headers,
            body=json.dumps(graphql_body),
            callback=self.parse_graphql_response,
            meta={'offset': offset, 'graphql_body': graphql_body}
        )

    def parse_graphql_response(self, response):
        """Parse GraphQL API response"""
        try:
            data = json.loads(response.text)
            
            if "errors" in data:
                self.logger.error(f"GraphQL errors: {data['errors']}")
                return
                
            if "data" not in data:
                self.logger.error("No data in GraphQL response")
                return
                
            search_result = data["data"]["searchQueries"]["search"]
            if "results" not in search_result:
                self.logger.error("No results in GraphQL response")
                return
                
            results = search_result["results"]
            self.logger.info(f"Found {len(results)} hotels in GraphQL response")
            
            for result in results:
                if result.get('__typename') == 'SearchResultProperty':
                    hotel_data = self.parse_graphql_hotel(result)
                    if hotel_data:
                        yield hotel_data
                        
            # Check if we should request more pages
            total_count = search_result.get("totalCount", 0)
            current_offset = response.meta.get('offset', 0)
            
            if current_offset + 25 < total_count and current_offset < 200:  # Limit to prevent too many requests
                next_offset = current_offset + 25
                graphql_body = response.meta['graphql_body']
                yield self.make_graphql_request(response, graphql_body, next_offset)
                
        except Exception as e:
            self.logger.error(f"Error parsing GraphQL response: {e}")

    def parse_graphql_hotel(self, result):
        """Parse hotel data from GraphQL result"""
        try:
            basic_data = result.get('basicPropertyData', {})
            price_info = result.get('priceDisplayInfoIrene', {})
            blocks = result.get('blocks', [])
            
            # Extract price
            price_amount = None
            price_currency = None
            
            if price_info and price_info.get('displayPrice'):
                price_amount = price_info['displayPrice'].get('amount')
                price_currency = price_info['displayPrice'].get('currency')
            elif blocks:
                for block in blocks:
                    if block.get('finalPrice'):
                        price_amount = block['finalPrice'].get('amount')
                        price_currency = block['finalPrice'].get('currency')
                        break
            
            hotel_data = {
                'id': basic_data.get('id'),
                'name': basic_data.get('name'),
                'location': basic_data.get('location', {}).get('displayLocation'),
                'rating_numeric': basic_data.get('reviewScore', {}).get('score'),
                'reviews_count_numeric': basic_data.get('reviewScore', {}).get('totalScoreCount'),
                'price_numeric': price_amount,
                'currency': price_currency,
                'page_name': basic_data.get('pageName'),
                'image_url': None,
                'source': 'graphql'
            }
            
            # Extract image URL
            photos = basic_data.get('photos', {})
            if photos and photos.get('main', {}).get('highResUrl'):
                hotel_data['image_url'] = photos['main']['highResUrl'].get('absoluteUrl')
            
            # Create booking URL
            if hotel_data['page_name']:
                hotel_data['url'] = f"https://www.booking.com/hotel/{hotel_data['page_name']}.html"
            
            return hotel_data
            
        except Exception as e:
            self.logger.error(f"Error parsing GraphQL hotel: {e}")
            return None

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Total results collected: {len(self.results)}")
