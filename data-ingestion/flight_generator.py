#!/usr/bin/env python3
"""
Standalone flight data generator with Kafka pipeline
"""

import sys
import os
from datetime import datetime
import random

# Add the scrapers directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scrapers'))

# Import our Kafka pipeline
from kafka_pipeline import KafkaPipeline

class MockSpider:
    """Mock spider for testing"""
    name = 'mock_flight_spider'
    
    class Logger:
        def info(self, msg):
            print(f"INFO: {msg}")
        def error(self, msg):
            print(f"ERROR: {msg}")
    
    logger = Logger()

def generate_flight_data():
    """Generate sample flight data and send to Kafka"""
    
    print("🚀 VoYatra Flight Data Generator with Kafka Streaming")
    print("🎯 Target: VM Kafka at 10.7.6.33:9092")
    print("-" * 60)
    
    # Create pipeline and mock spider
    pipeline = KafkaPipeline()
    spider = MockSpider()
    
    try:
        # Initialize pipeline
        print("🔌 Initializing Kafka pipeline...")
        pipeline.open_spider(spider)
        
        # Generate flight data
        airlines = ['Air India', 'IndiGo', 'SpiceJet', 'Vistara', 'GoAir']
        routes = [
            ('Delhi', 'Mumbai'),
            ('Bangalore', 'Hyderabad'),
            ('Chennai', 'Kolkata'),
            ('Pune', 'Goa'),
            ('Ahmedabad', 'Jaipur')
        ]
        
        print("✈️  Generating and sending flight data...")
        
        for i in range(5):
            source, destination = random.choice(routes)
            airline = random.choice(airlines)
            
            flight_data = {
                'flight_number': f'{random.choice(["AI", "6E", "SG", "UK", "G8"])}{random.randint(100, 999)}',
                'airline': airline,
                'source': source,
                'destination': destination,
                'departure_time': f'{random.randint(6, 22):02d}:{random.choice(["00", "30"])}',
                'arrival_time': f'{random.randint(8, 23):02d}:{random.choice(["00", "30"])}',
                'price': round(random.uniform(3000, 15000), 2),
                'duration': f'{random.randint(1, 4)}h {random.randint(0, 55)}m',
                'stops': random.choice(['Non-stop', '1 stop', '2 stops']),
                'scraped_at': datetime.now().isoformat(),
                'url': 'http://test-flight-generator.com'
            }
            
            print(f"\n🛫 Flight {i+1}: {flight_data['flight_number']}")
            print(f"   Route: {source} → {destination}")
            print(f"   Airline: {airline}")
            print(f"   Price: ₹{flight_data['price']:,.0f}")
            
            # Send through pipeline
            pipeline.process_item(flight_data, spider)
            
            # Small delay
            import time
            time.sleep(2)
        
        print("\n" + "="*60)
        print("✅ Flight data generation completed!")
        print("🔍 Check your VM Kafka consumer to see the data")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        try:
            pipeline.close_spider(spider)
        except:
            pass

if __name__ == "__main__":
    generate_flight_data()