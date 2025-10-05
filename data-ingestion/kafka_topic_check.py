#!/usr/bin/env python3
"""
Kafka topic checker and creator
"""

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
from datetime import datetime

def check_and_create_topic():
    """Check if flight-data topic exists and create if needed"""
    
    print("🔄 Checking Kafka topic 'flight-data' on VM...")
    print("🎯 Target: 10.7.6.33:9092")
    
    try:
        # Try to create admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=['10.7.6.33:9092'],
            request_timeout_ms=10000
        )
        
        print("✅ Admin client connected")
        
        # Try to create topic
        topic = NewTopic(name='flight-data', num_partitions=1, replication_factor=1)
        try:
            admin_client.create_topics([topic])
            print("✅ Topic 'flight-data' created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Topic 'flight-data' already exists")
            else:
                print(f"⚠️  Topic creation issue: {e}")
        
        admin_client.close()
        
        # Now try producer with minimal configuration
        print("\n🔄 Testing producer with simpler configuration...")
        
        producer = KafkaProducer(
            bootstrap_servers=['10.7.6.33:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            max_block_ms=5000,  # Only wait 5 seconds for metadata
            request_timeout_ms=5000  # 5 second timeout
        )
        
        print("✅ Producer created with simpler config")
        
        # Send a simple test message
        test_data = {
            'test': True,
            'message': 'Hello from VoYatra Windows!',
            'timestamp': datetime.now().isoformat()
        }
        
        print("📤 Sending test message...")
        future = producer.send('flight-data', test_data)
        
        # Don't wait for result, just send and close
        producer.flush(timeout=5)
        producer.close()
        
        print("✅ Test message sent! Check your VM consumer.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure Kafka is running on VM: sudo systemctl status kafka")
        print("   2. Check if port 9092 is open: sudo netstat -tlnp | grep 9092")
        print("   3. Verify VM IP is correct: 10.7.6.33")
        print("   4. Check VM firewall settings")
        return False

if __name__ == "__main__":
    check_and_create_topic()