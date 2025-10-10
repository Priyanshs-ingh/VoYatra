# VoYatra - Presentation Quick Reference

## 🎯 Project Overview
Real-time travel data ingestion system with Kafka streaming to VM for big data processing.

## 📁 Clean Directory Structure

```
data-ingestion/
├── scrapers/
│   ├── travel_scrapers/
│   │   ├── spiders/
│   │   │   ├── simple_flight_spider.py        # Test spider (generates fake data)
│   │   │   ├── flights_spider.py              # Template spider
│   │   │   ├── flights_spider_enhanced.py     # Advanced anti-bot spider
│   │   │   ├── amadeus_flight_spider.py       # API-based (RECOMMENDED)
│   │   │   ├── hotels_spider.py               # Hotel data spider
│   │   │   ├── news_spider.py                 # Travel news spider
│   │   │   └── weather_spider.py              # Weather data spider
│   │   ├── items.py                           # Data models
│   │   ├── pipelines.py                       # Data validation
│   │   └── settings.py                        # Scrapy configuration
│   ├── kafka_pipeline.py                      # Kafka streaming pipeline
│   └── SPIDERS_README.md                      # Spider documentation
├── scripts/
│   ├── start_scraping.py                      # Main entry point
│   ├── kafka_producer.py                      # Kafka producer
│   └── hdfs_uploader.py                       # HDFS integration
├── config/
│   ├── kafka_config.py                        # Kafka configuration
│   └── scraping_settings.py                   # Scraper settings
└── flight_generator.py                        # Standalone test generator
```

## 🚀 Key Features

### 1. Real-time Data Streaming
- **Kafka Integration**: Streams data to VM at `10.7.6.33:9092`
- **Topic**: `flight-data`
- **Pipeline**: Automatic data validation and streaming

### 2. Multiple Data Sources
- ✈️ **Flights**: 4 different spider approaches
- 🏨 **Hotels**: Hotel booking data
- 📰 **News**: Travel news and updates
- ☁️ **Weather**: Weather information

### 3. Production-Ready Architecture
- **Scalable**: Scrapy framework with concurrent requests
- **Reliable**: Error handling and retry mechanisms
- **Monitored**: Comprehensive logging
- **Flexible**: Easy to add new spiders

## 🎬 Demo Commands

### Test Data Generation (Quick Demo)
```bash
cd d:\VoYatra\data-ingestion\scrapers
scrapy crawl simple_flight
```
**Result**: Generates 3 test flights → Sends to Kafka → VM receives data

### Production Flight Scraping
```bash
cd d:\VoYatra\data-ingestion\scrapers
scrapy crawl flights_spider_enhanced
```

### Standalone Generator
```bash
cd d:\VoYatra\data-ingestion
python flight_generator.py
```

## 📊 Data Flow Architecture

```
┌─────────────┐
│   Windows   │
│  (Scrapers) │
└──────┬──────┘
       │ Scrapes flight data
       ▼
┌─────────────┐
│   Kafka     │
│  Pipeline   │  (kafka_pipeline.py)
└──────┬──────┘
       │ Real-time streaming
       ▼
┌─────────────┐
│     VM      │
│   Kafka     │  10.7.6.33:9092
│   Broker    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Consumer   │  (Your VM)
│ Processing  │
└─────────────┘
```

## 🔧 Configuration

### Kafka Settings (`kafka_pipeline.py`)
- **VM IP**: `10.7.6.33:9092`
- **Topic**: `flight-data`
- **Mode**: Fire-and-forget (acks=0)
- **Timeout**: 5 seconds

### Spider Settings (`settings.py`)
```python
ITEM_PIPELINES = {
    'kafka_pipeline.KafkaPipeline': 300,
}
```

## 📈 Key Metrics for Presentation

- **Spiders**: 7 different data collectors
- **Data Types**: Flights, Hotels, News, Weather
- **Streaming**: Real-time to Kafka
- **Architecture**: Windows → Kafka → VM
- **Framework**: Scrapy (Production-ready)

## ✅ Cleanup Status

- ✅ Removed 6 duplicate/test files
- ✅ Organized clear structure
- ✅ Production-ready spiders only
- ✅ Comprehensive documentation
- ✅ Working Kafka pipeline

## 🎤 Presentation Talking Points

1. **Problem**: Need real-time travel data for analytics
2. **Solution**: Distributed scraping with Kafka streaming
3. **Architecture**: Scrapy spiders → Kafka → VM processing
4. **Scalability**: Can add unlimited spiders and topics
5. **Reliability**: Error handling, retries, validation
6. **Flexibility**: Multiple data sources (flights, hotels, news, weather)

## 🚨 Live Demo Tips

1. **Start with**: `scrapy crawl simple_flight` (quick, guaranteed to work)
2. **Show**: Real-time Kafka streaming
3. **Explain**: How data flows to VM
4. **Highlight**: Clean architecture and scalability

Good luck with your presentation! 🎉