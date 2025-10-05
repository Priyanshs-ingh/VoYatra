# -*- coding: utf-8 -*-
from kafka import KafkaProducer
import json
import logging

class KafkaPipeline:
    """
    Pipeline to send scraped flight data to Kafka
    """
    
    def __init__(self):
        self.producer = None
        self.items_sent = 0
        
    def open_spider(self, spider):
        """Initialize Kafka producer when spider starts"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=['10.7.6.33:9092'],  # Your VM IP
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks=0,  # Don't wait for acknowledgment - fire and forget
                retries=1,   # Minimal retries
                max_block_ms=5000,  # Only wait 5 seconds for metadata
                request_timeout_ms=5000,  # 5 second timeout
                linger_ms=1000,  # Batch messages for better performance
                batch_size=16384  # Reasonable batch size
            )
            spider.logger.info("✅ Connected to Kafka on VM (10.7.6.33:9092)")
        except Exception as e:
            spider.logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def close_spider(self, spider):
        """Close Kafka producer when spider finishes"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            spider.logger.info(f"✅ Kafka connection closed. Total items sent: {self.items_sent}")
    
    def process_item(self, item, spider):
        """Send each scraped item to Kafka topic"""
        try:
            # Convert Scrapy item to dictionary
            item_dict = dict(item)
            
            # Send to Kafka topic 'flight-data' without waiting for response
            self.producer.send('flight-data', item_dict)
            
            self.items_sent += 1
            spider.logger.info(f"✅ Sent to Kafka: {item_dict.get('flight_number', 'Unknown')} ({item_dict.get('source', '')} → {item_dict.get('destination', '')})")
            
        except Exception as e:
            spider.logger.error(f"❌ Failed to send to Kafka: {e}")
            # Don't raise exception - continue scraping even if Kafka fails
        
        return item