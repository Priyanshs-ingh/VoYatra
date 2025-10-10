# VoYatra Flight Spiders - Production Ready

## Available Spiders

### 1. **simple_flight** (Test/Demo Spider)
- **File**: `simple_flight_spider.py`
- **Purpose**: Generate test flight data for Kafka pipeline testing
- **Usage**: `scrapy crawl simple_flight`
- **Best For**: Testing your data pipeline without hitting real websites

### 2. **flight_spider** (Template Spider)
- **File**: `flights_spider.py`
- **Purpose**: Template for scraping actual flight booking websites
- **Usage**: `scrapy crawl flight_spider`
- **Data Source**: Customizable (update selectors for target website)
- **Best For**: Adapting to specific flight booking sites

### 3. **flights_spider_enhanced** (Advanced Spider)
- **File**: `flights_spider_enhanced.py`
- **Purpose**: Advanced scraping with anti-bot measures
- **Usage**: `scrapy crawl flights_spider_enhanced`
- **Features**:
  - Playwright browser automation
  - Random delays and user agents
  - Advanced anti-detection
- **Best For**: Scraping protected flight booking sites

### 4. **amadeus_flight_spider** (API-Based - RECOMMENDED)
- **File**: `amadeus_flight_spider.py`
- **Purpose**: Use Amadeus Flight API for reliable data
- **Usage**: `scrapy crawl amadeus_flight_spider`
- **Requirements**: Amadeus API credentials
- **Data Source**: Official Amadeus Flight API
- **Best For**: Production use, reliable and legal data access

## Kafka Integration

All spiders are configured to send data to Kafka topic `flight-data` on VM `10.7.6.33:9092`

### Running a Spider

```bash
# Navigate to scrapers directory
cd d:\VoYatra\data-ingestion\scrapers

# Run test spider (generates fake data)
scrapy crawl simple_flight

# Run enhanced spider
scrapy crawl flights_spider_enhanced
```

## Data Flow

```
Spider → Kafka Pipeline → VM Kafka Broker (10.7.6.33:9092) → Consumer
```

## Configuration

- **Kafka Pipeline**: `scrapers/kafka_pipeline.py`
- **Settings**: `scrapers/travel_scrapers/settings.py`
- **Items**: `scrapers/travel_scrapers/items.py`

## Presentation-Ready Status ✅

- ✅ Duplicate files removed
- ✅ Clean directory structure
- ✅ Working Kafka pipeline
- ✅ Test spider available
- ✅ Production-ready spiders documented