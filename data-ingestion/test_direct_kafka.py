#!/usr/bin/env python3
"""
Simple direct test of Kafka connection with exact IP
"""

from kafka import KafkaProducer
import json
from datetime import datetime

def test_direct_kafka():
    print("🔄 Testing direct Kafka connection...")
    print("🎯 Target: 10.7.6.33:9092")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=['10.7.6.33:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1,
            request_timeout_ms=10000  # 10 seconds timeout
        )
        
        print("✅ Producer created successfully")
        
        # Send test message
        test_data = {
            'flight_number': 'TEST123',
            'airline': 'Test Airline',
            'source': 'DEL',
            'destination': 'BOM',
            'price': 5000,
            'test_time': datetime.now().isoformat()
        }
        
        print("📤 Sending test message...")
        future = producer.send('flight-data', test_data)
        record = future.get(timeout=10)
        
        print(f"✅ Message sent successfully!")
        print(f"   Topic: {record.topic}")
        print(f"   Partition: {record.partition}")
        print(f"   Offset: {record.offset}")
        
        producer.flush()
        producer.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_direct_kafka()