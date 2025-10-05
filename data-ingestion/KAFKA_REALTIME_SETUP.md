# VoYatra Real-time Flight Data Streaming Setup

## Overview
This setup enables real-time streaming of flight scraping data from your Windows machine to the VM's Kafka broker for further processing.

## Architecture
```
Windows (VoYatra) → Kafka Producer → VM (10.7.6.33:9092) → Kafka Consumer → Processing
```

## Components Added

### 1. Kafka Pipeline (`travel_scrapers/pipelines.py`)
- **KafkaPipeline**: Sends scraped flight data to VM Kafka in real-time
- **Configuration**: Uses `kafka_config.py` for connection settings
- **Error Handling**: Robust error handling with logging and fallback
- **Topics**: Sends data to `flight-data` topic

### 2. Configuration (`config/kafka_config.py`)
- **Broker Settings**: VM IP and port configuration
- **Performance**: Compression and timeout settings
- **Topics**: Centralized topic management
- **Retry Logic**: Connection retry configuration

### 3. Updated Settings (`travel_scrapers/settings.py`)
- **Pipeline Order**: 
  1. DataValidationPipeline (200) - Validate data
  2. KafkaPipeline (250) - Send to VM
  3. JsonWriterPipeline (300) - Local backup
- **Logging**: Enhanced logging for Kafka operations

### 4. Dependencies (`requirements.txt`)
- Added `kafka-python>=2.0.2` for Kafka integration

### 5. Test Scripts
- **test_kafka_connection.py**: Test VM Kafka connectivity
- **start_realtime_scraping.py**: Start scraping with real-time streaming

## Usage

### Start Real-time Scraping
```bash
cd d:\VoYatra\data-ingestion\scripts
python start_realtime_scraping.py
```

### Test Kafka Connection
```bash
cd d:\VoYatra\data-ingestion\scripts
python test_kafka_connection.py
```

### Manual Scrapy with Kafka
```bash
cd d:\VoYatra\data-ingestion\scrapers
scrapy crawl flights_simple
```

## Data Flow

1. **Scraping**: Flight data is scraped from various sources
2. **Validation**: Data passes through DataValidationPipeline
3. **Kafka Streaming**: KafkaPipeline sends data to VM in real-time
4. **Local Backup**: JsonWriterPipeline saves data locally as backup
5. **VM Processing**: VM Kafka receives and processes the data

## Configuration Details

### VM Kafka Broker
- **IP**: 10.7.6.33
- **Port**: 9092
- **Topic**: flight-data

### Pipeline Settings
- **Compression**: gzip (reduces network usage)
- **Retries**: 3 attempts for failed sends
- **Timeout**: 30 seconds for requests
- **Acknowledgment**: Wait for leader acknowledgment

## Monitoring

### Logs Location
- **Scrapy Logs**: `data-ingestion/logs/scrapy/scrapy.log`
- **Kafka Events**: Logged in Scrapy logs with ✅/❌ indicators

### Success Indicators
- `✅ Connected to Kafka on VM`
- `✅ Sent to Kafka: DEL -> BOM`
- `✅ Kafka connection closed`

### Error Indicators
- `❌ Failed to connect to Kafka`
- `❌ Error sending to Kafka`
- `⚠️ Kafka producer not available`

## Troubleshooting

### Connection Issues
1. **Check VM Status**: Ensure VM is running and accessible
2. **Verify Kafka**: Confirm Kafka is running on VM port 9092
3. **Network**: Check Windows firewall and network connectivity
4. **IP Address**: Verify VM IP (10.7.6.33) is correct

### Data Issues
1. **Topic Creation**: Ensure `flight-data` topic exists on VM
2. **Permissions**: Check Kafka permissions for the topic
3. **Data Format**: Verify JSON serialization is working

### Performance Issues
1. **Timeout**: Increase `request_timeout_ms` in config
2. **Retries**: Adjust retry settings for unstable connections
3. **Compression**: Toggle compression if network is fast

## Benefits

1. **Real-time Processing**: Data flows immediately to VM for processing
2. **Reliability**: Local backup ensures no data loss
3. **Scalability**: Kafka handles high-throughput data streams
4. **Monitoring**: Comprehensive logging for debugging
5. **Configuration**: Centralized config for easy maintenance

## Next Steps

1. **VM Consumer**: Set up Kafka consumer on VM to process incoming data
2. **Data Processing**: Implement real-time analytics on VM
3. **Storage**: Configure VM to store processed data
4. **Monitoring**: Set up monitoring dashboards for data flow
5. **Scaling**: Add more spiders and topics as needed