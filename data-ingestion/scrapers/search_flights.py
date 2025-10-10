# -*- coding: utf-8 -*-
"""
Simple Flight Search - Sends data to Kafka on VM
"""
import sys
sys.path.insert(0, '.')

from kafka import KafkaProducer
import json
from datetime import datetime

def search_flights(source, destination):
    """Search flights and send to Kafka"""
    
    print(f"\n🔍 Searching flights: {source} → {destination}")
    
    # Connect to Kafka on VM
    producer = KafkaProducer(
        bootstrap_servers=['10.7.6.33:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Generate flight data
    flight_data = {
        'flight_number': 'AI450',
        'airline': 'Air India',
        'source': source,
        'destination': destination,
        'departure_time': '10:30',
        'arrival_time': '12:45',
        'price': 4500.0,
        'duration': '2h 15m',
        'stops': 'Non-stop',
        'scraped_at': datetime.now().isoformat(),
        'search_query': f'{source} to {destination}'
    }
    
    # Send to Kafka
    producer.send('flight-data', flight_data)
    producer.flush()
    producer.close()
    
    print(f"✅ Flight data sent to Kafka!")
    print(f"   From: {source}")
    print(f"   To: {destination}")
    print(f"   Flight: {flight_data['flight_number']}")
    print(f"   Price: ₹{flight_data['price']}")
    print(f"\n📊 Check VM Kafka to see your data!")

if __name__ == '__main__':
    # Get user input
    print("\n" + "="*50)
    print("   VOYATRA FLIGHT SEARCH")
    print("="*50)
    
    source = input("\n✈️  Enter SOURCE city: ").strip()
    destination = input("✈️  Enter DESTINATION city: ").strip()
    
    if source and destination:
        search_flights(source, destination)
    else:
        print("❌ Please enter both source and destination!")
