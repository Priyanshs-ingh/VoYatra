# Kafka Configuration for VoYatra Real-time Data Streaming

# VM Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap_servers': ['10.7.6.33:9092'],  # Your VM IP and Kafka port
    'retries': 3,
    'request_timeout_ms': 30000,
    'value_serializer': 'json',  # Will be handled in pipeline
    'acks': 1,  # Wait for leader acknowledgment
    'compression_type': 'gzip',  # Compress data for better network performance
}

# Topics Configuration
KAFKA_TOPICS = {
    'flight_data': 'flight-data',
    'hotel_data': 'hotel-data', 
    'weather_data': 'weather-data',
    'news_data': 'news-data'
}

# Connection retry settings
KAFKA_RETRY_CONFIG = {
    'max_retries': 5,
    'retry_backoff_ms': 100,
    'reconnect_backoff_ms': 50
}