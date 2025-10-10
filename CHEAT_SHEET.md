# 🎯 VoYatra Quick Reference Cheat Sheet

## 📁 Essential Files - What Each Does

| File | Purpose | Key Function |
|------|---------|--------------|
| **items.py** | 📋 Data Model | Defines FlightItem structure (11 fields) |
| **settings.py** | ⚙️ Configuration | Activates Kafka pipeline |
| **kafka_pipeline.py** | 🔌 Kafka Bridge | **SENDS DATA TO VM** |
| **simple_flight_spider.py** | ⚡ Test Spider | Generates 3 test flights |
| **flights_spider.py** | 📝 Template | Customizable scraper template |
| **flights_spider_enhanced.py** | 🛡️ Advanced | Anti-bot protection |
| **amadeus_flight_spider.py** | 🌟 API | Professional API-based |
| **flight_generator.py** | 🔧 Standalone | Test Kafka without Scrapy |

---

## 🔗 Data Flow in 5 Steps

```
1. Spider yields data
   ↓
2. settings.py routes to kafka_pipeline.py
   ↓
3. kafka_pipeline converts to JSON
   ↓
4. producer.send('flight-data', data) → 10.7.6.33:9092
   ↓
5. VM Kafka stores in 'flight-data' topic
```

---

## 🔑 Critical Code Lines

### 1. **WHERE Kafka connection happens**
**File**: `kafka_pipeline.py` Line 18
```python
self.producer = KafkaProducer(
    bootstrap_servers=['10.7.6.33:9092'],  # ← VM IP
```

### 2. **WHERE data is sent**
**File**: `kafka_pipeline.py` Line 48
```python
self.producer.send('flight-data', item_dict)  # ← KAFKA SEND!
#                   ^^^^^^^^^^^  ^^^^^^^^^^^
#                   TOPIC        DATA
```

### 3. **WHERE pipeline is activated**
**File**: `settings.py` Line 12
```python
ITEM_PIPELINES = {
    'kafka_pipeline.KafkaPipeline': 300,  # ← Enables Kafka
}
```

### 4. **WHERE data structure is defined**
**File**: `items.py` Line 4
```python
class FlightItem(scrapy.Item):
    flight_number = scrapy.Field()  # ← 11 fields defined
    airline = scrapy.Field()
    # ... more fields
```

### 5. **WHERE data originates**
**File**: `simple_flight_spider.py` Line 20
```python
def parse(self, response):
    yield {  # ← Data generated here
        'flight_number': 'AI303',
        'airline': 'Air India',
        # ...
    }
```

---

## 🎬 Demo Commands

```bash
# 1. See available spiders
cd d:\VoYatra\data-ingestion\scrapers
scrapy list

# 2. Run test spider (3 flights → Kafka)
scrapy crawl simple_flight

# 3. Run standalone generator (5 flights → Kafka)
cd d:\VoYatra\data-ingestion
python flight_generator.py

# 4. Check logs
cd d:\VoYatra\data-ingestion\logs\scrapy
type scrapy.log
```

---

## 🔧 Kafka Configuration Explained

```python
KafkaProducer(
    bootstrap_servers=['10.7.6.33:9092'],
    # ↑ WHERE: VM IP and port
    
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    # ↑ HOW: Convert Python dict → JSON → bytes
    
    acks=0,
    # ↑ SPEED: Don't wait for confirmation (fire-and-forget)
    
    max_block_ms=5000,
    # ↑ TIMEOUT: Wait max 5 seconds
    
    batch_size=16384
    # ↑ EFFICIENCY: Batch up to 16KB of messages
)
```

---

## 📊 Data at Each Stage

| Stage | Format | Example |
|-------|--------|---------|
| **1. Spider** | Python dict | `{'flight_number': 'AI303', ...}` |
| **2. Pipeline** | Python dict | `{'flight_number': 'AI303', ...}` |
| **3. Serialized** | JSON string | `'{"flight_number":"AI303",...}'` |
| **4. Network** | Bytes | `b'{"flight_number":"AI303",...}'` |
| **5. Kafka** | Stored bytes | Binary on disk |
| **6. Consumer** | JSON string | `{"flight_number":"AI303",...}` |

---

## 🎯 Three Execution Methods

### Method 1: Scrapy Spider (Production)
```bash
cd d:\VoYatra\data-ingestion\scrapers
scrapy crawl simple_flight
```
**Uses**: Full Scrapy framework + Kafka pipeline

### Method 2: Standalone Generator (Testing)
```bash
cd d:\VoYatra\data-ingestion
python flight_generator.py
```
**Uses**: Just kafka_pipeline.py directly

### Method 3: Custom Spider (Development)
```bash
cd d:\VoYatra\data-ingestion\scrapers
scrapy crawl flights_spider_enhanced
```
**Uses**: Advanced spider + Kafka pipeline

---

## 🔍 Troubleshooting Quick Guide

| Issue | File to Check | Line to Check |
|-------|--------------|---------------|
| No Kafka connection | `kafka_pipeline.py` | Line 18 (bootstrap_servers) |
| Wrong topic | `kafka_pipeline.py` | Line 48 (topic name) |
| Pipeline not running | `settings.py` | Line 12 (ITEM_PIPELINES) |
| Wrong data fields | `items.py` | Line 4-15 (FlightItem) |
| No data generated | Spider files | parse() method |

---

## 📋 Kafka Pipeline Lifecycle

```
1. open_spider(spider)
   ├─ Creates KafkaProducer
   ├─ Connects to 10.7.6.33:9092
   └─ Logs: "✅ Connected to Kafka on VM"

2. process_item(item, spider)  [Called for EACH item]
   ├─ Converts item to dict
   ├─ Sends to Kafka topic
   └─ Logs: "✅ Sent to Kafka: AI303"

3. close_spider(spider)
   ├─ Flushes remaining messages
   ├─ Closes Kafka connection
   └─ Logs: "✅ Kafka connection closed. Total: 3"
```

---

## 🎤 Presentation Talking Points

### 1. **Data Source**
"Data comes from spiders like `simple_flight_spider.py` which scrape or generate flight information"

### 2. **Data Structure**
"All flight data follows the `FlightItem` model defined in `items.py` with 11 fields"

### 3. **Kafka Bridge**
"`kafka_pipeline.py` is the critical bridge that connects Scrapy to Kafka on the VM"

### 4. **Pipeline Activation**
"`settings.py` tells Scrapy to use the Kafka pipeline with this one line: `ITEM_PIPELINES`"

### 5. **Data Transfer**
"When `producer.send('flight-data', data)` is called, data is sent to VM at 10.7.6.33:9092"

### 6. **Real-Time Processing**
"VM Kafka consumers can read this data in real-time for analytics and processing"

---

## 🚀 Quick Test Sequence

```bash
# Step 1: Navigate
cd d:\VoYatra\data-ingestion\scrapers

# Step 2: Run spider
scrapy crawl simple_flight

# Expected Output:
# ✅ Connected to Kafka on VM (10.7.6.33:9092)
# ✅ Sent to Kafka: AI303 (Delhi → Mumbai)
# ✅ Sent to Kafka: AI456 (Delhi → Mumbai)
# ✅ Sent to Kafka: AI789 (Delhi → Mumbai)
# ✅ Kafka connection closed. Total items sent: 3

# Step 3: Check on VM
# kafka-console-consumer --bootstrap-server localhost:9092 \
#   --topic flight-data --from-beginning
```

---

## 🔢 By the Numbers

- **7 Spiders**: Different data sources
- **4 Flight Spiders**: Different scraping approaches
- **1 Pipeline**: Kafka connection (kafka_pipeline.py)
- **1 Topic**: 'flight-data' on VM
- **11 Fields**: In FlightItem model
- **3 Test Flights**: Generated by simple_flight
- **~250 bytes**: Per flight message

---

## 💡 Remember These Key Concepts

1. **Spider** = Data Source (WHERE data comes from)
2. **Items** = Data Model (WHAT data looks like)
3. **Settings** = Pipeline Config (WHICH pipeline to use)
4. **Kafka Pipeline** = Bridge (HOW data transfers)
5. **Producer.send()** = The Moment (WHEN data goes to Kafka)
6. **VM Kafka** = Destination (WHERE data ends up)

---

## 🎯 One-Liner Explanations

| Component | One-Liner |
|-----------|-----------|
| **items.py** | "Blueprint for flight data structure" |
| **settings.py** | "Activates Kafka pipeline for all spiders" |
| **kafka_pipeline.py** | "Sends every scraped item to VM Kafka" |
| **simple_flight** | "Generates 3 test flights for demo" |
| **flight_generator** | "Standalone Kafka test without Scrapy" |
| **producer.send()** | "The actual line that sends data to VM" |
| **10.7.6.33:9092** | "VM IP and Kafka port" |
| **'flight-data'** | "Kafka topic name where data is stored" |

---

**Print this cheat sheet for your presentation! 🎯**