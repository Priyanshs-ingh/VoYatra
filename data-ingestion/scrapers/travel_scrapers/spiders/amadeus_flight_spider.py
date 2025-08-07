"""
Amadeus API Flight Search Implementation
This is the RECOMMENDED approach for reliable flight data without bot blocks
"""

import requests
import json
from datetime import datetime, timedelta
from ..items import FlightItem
import scrapy

class AmadeusFlightSpider(scrapy.Spider):
    name = 'amadeus_flight_spider'
    
    # Amadeus API Configuration
    AMADEUS_API_KEY = "YOUR_API_KEY_HERE"  # Get from https://developers.amadeus.com/
    AMADEUS_API_SECRET = "YOUR_API_SECRET_HERE"
    AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
    AMADEUS_FLIGHT_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    
    def __init__(self, origin=None, destination=None, departure_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin or 'DEL'
        self.destination = destination or 'BOM'
        self.departure_date = departure_date or self._get_tomorrow_date()
        self.access_token = None
    
    def _get_tomorrow_date(self):
        return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    def start_requests(self):
        """Get access token first, then search flights"""
        yield scrapy.Request(
            url="https://httpbin.org/get",  # Dummy request to start the spider
            callback=self.get_access_token
        )
    
    def get_access_token(self, response):
        """Get Amadeus API access token"""
        try:
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': self.AMADEUS_API_KEY,
                'client_secret': self.AMADEUS_API_SECRET
            }
            
            token_response = requests.post(self.AMADEUS_TOKEN_URL, data=token_data)
            if token_response.status_code == 200:
                self.access_token = token_response.json()['access_token']
                self.logger.info("✅ Amadeus API token obtained successfully")
                
                # Now search for flights
                return self.search_flights()
            else:
                self.logger.error(f"❌ Failed to get Amadeus token: {token_response.text}")
                
        except Exception as e:
            self.logger.error(f"❌ Token request error: {str(e)}")
    
    def search_flights(self):
        """Search flights using Amadeus API"""
        if not self.access_token:
            self.logger.error("❌ No access token available")
            return
            
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'originLocationCode': self.origin,
            'destinationLocationCode': self.destination,
            'departureDate': self.departure_date,
            'adults': 1,
            'max': 10  # Limit results
        }
        
        try:
            response = requests.get(self.AMADEUS_FLIGHT_URL, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                self.logger.info(f"✅ Found {len(data.get('data', []))} flights")
                
                for offer in data.get('data', []):
                    item = self.parse_flight_offer(offer)
                    if item:
                        yield item
            else:
                self.logger.error(f"❌ Flight search failed: {response.text}")
                
        except Exception as e:
            self.logger.error(f"❌ Flight search error: {str(e)}")
    
    def parse_flight_offer(self, offer):
        """Parse Amadeus flight offer data"""
        try:
            # Extract itinerary information
            itineraries = offer.get('itineraries', [])
            if not itineraries:
                return None
                
            first_itinerary = itineraries[0]
            segments = first_itinerary.get('segments', [])
            if not segments:
                return None
                
            first_segment = segments[0]
            last_segment = segments[-1]
            
            # Extract airline information
            airline_code = first_segment.get('carrierCode', '')
            
            # Extract pricing
            price_info = offer.get('price', {})
            total_price = price_info.get('total', '')
            currency = price_info.get('currency', 'EUR')
            
            # Extract timing
            departure_time = first_segment.get('departure', {}).get('at', '')
            arrival_time = last_segment.get('arrival', {}).get('at', '')
            
            # Calculate duration
            duration = first_itinerary.get('duration', '')
            
            # Create flight item
            item = FlightItem()
            item['source'] = 'Amadeus API'
            item['airline'] = airline_code
            item['price'] = f"{total_price} {currency}"
            item['departure_time'] = departure_time
            item['arrival_time'] = arrival_time
            item['duration'] = duration
            item['origin'] = self.origin
            item['destination'] = self.destination
            item['departure_date'] = self.departure_date
            item['flight_number'] = first_segment.get('number', '')
            item['aircraft'] = first_segment.get('aircraft', {}).get('code', '')
            item['data_type'] = 'flights'
            item['scraped_at'] = datetime.now().isoformat()
            
            return item
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing flight offer: {str(e)}")
            return None


# Standalone function for easy testing
def search_flights_amadeus(origin, destination, departure_date, api_key, api_secret):
    """
    Standalone function to search flights using Amadeus API
    Usage example:
    
    flights = search_flights_amadeus('DEL', 'BOM', '2025-08-12', 'your_key', 'your_secret')
    """
    
    # Get access token
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            print(f"❌ Failed to get token: {token_response.text}")
            return []
            
        access_token = token_response.json()['access_token']
        print("✅ Access token obtained")
        
        # Search flights
        flight_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'originLocationCode': origin,
            'destinationLocationCode': destination,
            'departureDate': departure_date,
            'adults': 1,
            'max': 5
        }
        
        flight_response = requests.get(flight_url, headers=headers, params=params)
        
        if flight_response.status_code == 200:
            data = flight_response.json()
            flights = data.get('data', [])
            print(f"✅ Found {len(flights)} flights")
            
            # Display results
            for i, flight in enumerate(flights, 1):
                price = flight.get('price', {})
                itinerary = flight.get('itineraries', [{}])[0]
                segment = itinerary.get('segments', [{}])[0]
                
                print(f"\n🛩️  Flight {i}:")
                print(f"   Airline: {segment.get('carrierCode', 'N/A')}")
                print(f"   Price: {price.get('total', 'N/A')} {price.get('currency', '')}")
                print(f"   Departure: {segment.get('departure', {}).get('at', 'N/A')}")
                print(f"   Duration: {itinerary.get('duration', 'N/A')}")
            
            return flights
        else:
            print(f"❌ Flight search failed: {flight_response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return []


if __name__ == "__main__":
    # Example usage
    print("🛩️  Amadeus API Flight Search Demo")
    print("=" * 50)
    print("📝 To use this:")
    print("1. Sign up at https://developers.amadeus.com/")
    print("2. Get your API key and secret")
    print("3. Replace 'YOUR_API_KEY_HERE' and 'YOUR_API_SECRET_HERE'")
    print("4. Run: python -m scrapy crawl amadeus_flight_spider -a origin=DEL -a destination=BOM")
    print()
    print("✨ This approach has:")
    print("   ✅ No bot detection")
    print("   ✅ Reliable data")
    print("   ✅ 2000 free requests/month")
    print("   ✅ Structured JSON responses")
    print("   ✅ Real-time pricing")
