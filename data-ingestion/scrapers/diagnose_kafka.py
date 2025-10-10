# -*- coding: utf-8 -*-
"""
Kafka Connection Diagnostic Tool
Tests connection and identifies issues
"""
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import socket

def test_network():
    """Test basic network connectivity"""
    print("=" * 60)
    print("STEP 1: Testing Network Connectivity")
    print("=" * 60)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('10.7.6.33', 9092))
        sock.close()
        
        if result == 0:
            print("✅ Network connection to 10.7.6.33:9092 is WORKING")
            return True
        else:
            print("❌ Cannot connect to 10.7.6.33:9092")
            print("   Fix: Check if VM Kafka is running")
            return False
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

def test_kafka_producer():
    """Test Kafka producer connection"""
    print("\n" + "=" * 60)
    print("STEP 2: Testing Kafka Producer")
    print("=" * 60)
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=['10.7.6.33:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks=0,
            max_block_ms=10000,
            request_timeout_ms=10000,
            api_version=(0, 10, 1)  # Match your Kafka version
        )
        
        print("✅ Kafka Producer created successfully")
        
        # Get cluster metadata
        metadata = producer._metadata
        print(f"\n📊 Cluster Metadata:")
        print(f"   Brokers: {metadata.brokers()}")
        
        # Try to send a test message
        test_flight = {
            'flight_number': 'TEST001',
            'airline': 'Test Airlines',
            'source': 'Windows',
            'destination': 'VM',
            'price': 1.0
        }
        
        print("\n🚀 Sending test message...")
        future = producer.send('flight-data', test_flight)
        
        try:
            record_metadata = future.get(timeout=10)
            print(f"✅ Message sent successfully!")
            print(f"   Topic: {record_metadata.topic}")
            print(f"   Partition: {record_metadata.partition}")
            print(f"   Offset: {record_metadata.offset}")
            producer.flush()
            producer.close()
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            print(f"\n🔍 DIAGNOSIS:")
            print(f"   The broker is advertising wrong address.")
            print(f"   You need to fix server.properties on VM.")
            print(f"   See fix_kafka_vm.md for instructions.")
            producer.close()
            return False
            
    except Exception as e:
        print(f"❌ Failed to create Kafka producer: {e}")
        return False

def main():
    print("\n🔍 KAFKA CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Test 1: Network
    network_ok = test_network()
    
    if not network_ok:
        print("\n❌ FAILED: Cannot connect to VM")
        print("   Action: Check VM is running and Kafka is started")
        return
    
    # Test 2: Kafka Producer
    kafka_ok = test_kafka_producer()
    
    if kafka_ok:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Everything is working!")
        print("=" * 60)
        print("\nYou can now run: python run_spider.py")
    else:
        print("\n" + "=" * 60)
        print("⚠️  FIX REQUIRED")
        print("=" * 60)
        print("\n📝 Action Required:")
        print("   1. SSH to VM: ssh cloudera@10.7.6.33")
        print("   2. Edit: /home/cloudera/kafka_2.11-0.10.1.0/config/server.properties")
        print("   3. Add: advertised.listeners=PLAINTEXT://10.7.6.33:9092")
        print("   4. Restart Kafka")
        print("\n   See fix_kafka_vm.md for detailed steps")

if __name__ == '__main__':
    main()
