# 🎨 VoYatra Visual Data Flow Diagrams

## 🔄 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WINDOWS MACHINE                          │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              SCRAPY FRAMEWORK                          │   │
│  │                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │   │
│  │  │ Spider Files │  │   items.py   │  │ settings.py │ │   │
│  │  │              │  │              │  │             │ │   │
│  │  │ • simple_    │  │ FlightItem   │  │ PIPELINES={ │ │   │
│  │  │   flight     │  │ =========    │  │  kafka: 300 │ │   │
│  │  │ • enhanced   │  │ -flight_num  │  │ }           │ │   │
│  │  │ • amadeus    │  │ -airline     │  │             │ │   │
│  │  │              │  │ -source      │  │             │ │   │
│  │  └──────┬───────┘  └──────────────┘  └─────────────┘ │   │
│  │         │                                             │   │
│  │         │ yields FlightItem                           │   │
│  │         ▼                                             │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │      KAFKA PIPELINE (kafka_pipeline.py)     │     │   │
│  │  │                                              │     │   │
│  │  │  1. open_spider()                            │     │   │
│  │  │     → Connect to Kafka                       │     │   │
│  │  │                                              │     │   │
│  │  │  2. process_item()                           │     │   │
│  │  │     → Convert to JSON                        │     │   │
│  │  │     → Send to Kafka topic                    │     │   │
│  │  │                                              │     │   │
│  │  │  3. close_spider()                           │     │   │
│  │  │     → Flush & Close connection               │     │   │
│  │  └─────────────────┬───────────────────────────┘     │   │
│  └────────────────────┼─────────────────────────────────┘   │
│                       │                                       │
│                       │ TCP Connection                        │
│                       │ 10.7.6.33:9092                        │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        │ Network
                        │
┌───────────────────────▼───────────────────────────────────────┐
│                        LINUX VM                               │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            KAFKA BROKER (Port 9092)                 │    │
│  │                                                     │    │
│  │  Topic: 'flight-data'                               │    │
│  │  ┌───────────────────────────────────────────┐     │    │
│  │  │  Partition 0                              │     │    │
│  │  │  [msg1][msg2][msg3][msg4]...             │     │    │
│  │  └───────────────────────────────────────────┘     │    │
│  └─────────────────────┬───────────────────────────────┘    │
│                        │                                      │
│                        │ read messages                        │
│                        ▼                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         KAFKA CONSUMER                              │    │
│  │                                                     │    │
│  │  kafka-console-consumer --topic flight-data        │    │
│  │  [Displays flight data in real-time]               │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

---

## 🔀 Data Transformation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: SPIDER GENERATES DATA                                  │
└─────────────────────────────────────────────────────────────────┘

    simple_flight_spider.py
    
    def parse(self, response):
        yield {
            'flight_number': 'AI303',
            'airline': 'Air India',
            'source': 'Delhi',
            'destination': 'Mumbai',
            'price': 4500.0
        }
    
    ↓ (Python Dictionary)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: SCRAPY CREATES FlightItem OBJECT                       │
└─────────────────────────────────────────────────────────────────┘

    FlightItem(
        flight_number='AI303',
        airline='Air India',
        source='Delhi',
        destination='Mumbai',
        price=4500.0
    )
    
    ↓ (Scrapy Item Object)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: PIPELINE RECEIVES ITEM                                 │
└─────────────────────────────────────────────────────────────────┘

    kafka_pipeline.py
    
    def process_item(self, item, spider):
        item_dict = dict(item)  # Convert to dict
        
    ↓ (Python Dictionary)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: JSON SERIALIZATION                                     │
└─────────────────────────────────────────────────────────────────┘

    value_serializer=lambda v: json.dumps(v).encode('utf-8')
    
    {
        "flight_number": "AI303",
        "airline": "Air India",
        "source": "Delhi",
        "destination": "Mumbai",
        "price": 4500.0
    }
    
    ↓ (JSON String → UTF-8 Bytes)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: KAFKA SEND                                             │
└─────────────────────────────────────────────────────────────────┘

    producer.send('flight-data', item_dict)
    
    ↓ (Network Packet)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6: KAFKA BROKER STORAGE                                   │
└─────────────────────────────────────────────────────────────────┘

    Stored in 'flight-data' topic
    Partition 0, Offset 12345
    
    ↓ (Persistent Storage)

┌─────────────────────────────────────────────────────────────────┐
│ STAGE 7: CONSUMER READS                                         │
└─────────────────────────────────────────────────────────────────┘

    kafka-console-consumer reads message
    Displays JSON on VM terminal
```

---

## ⚙️ Pipeline Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                 SCRAPY STARTUP SEQUENCE                          │
└─────────────────────────────────────────────────────────────────┘

1. User runs: scrapy crawl simple_flight
   │
   ▼
2. Scrapy loads settings.py
   │ Reads: ITEM_PIPELINES = {'kafka_pipeline.KafkaPipeline': 300}
   ▼
3. Scrapy imports kafka_pipeline.py
   │ Creates: pipeline = KafkaPipeline()
   ▼
4. Scrapy loads spider: simple_flight
   │ Creates: spider = SimpleFlightSpider()
   ▼
5. Scrapy calls: pipeline.open_spider(spider)
   │ Executes: self.producer = KafkaProducer(...)
   │ Result: ✅ Connected to Kafka on VM (10.7.6.33:9092)
   ▼
6. Spider starts: spider.start_requests()
   │ Makes HTTP request (or generates data)
   ▼
7. Spider yields item: yield {'flight_number': 'AI303', ...}
   │
   ▼
8. Scrapy calls: pipeline.process_item(item, spider)
   │ Executes: self.producer.send('flight-data', item_dict)
   │ Result: ✅ Sent to Kafka: AI303 (Delhi → Mumbai)
   ▼
9. Repeat steps 7-8 for each item
   │
   ▼
10. Spider finishes
    │
    ▼
11. Scrapy calls: pipeline.close_spider(spider)
    │ Executes: self.producer.flush()
    │ Executes: self.producer.close()
    │ Result: ✅ Kafka connection closed. Total items sent: 3
    ▼
12. Done!
```

---

## 🔌 Kafka Connection Details

```
┌─────────────────────────────────────────────────────────────────┐
│             KAFKA PRODUCER INITIALIZATION                        │
└─────────────────────────────────────────────────────────────────┘

    KafkaProducer(
        bootstrap_servers=['10.7.6.33:9092'],
        │                   └─────┬─────┘
        │                         │
        │                         └─→ VM IP Address:Port
        │
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        │                          └──────┬──────┘
        │                                 │
        │                                 └─→ Convert Python → JSON
        │
        acks=0,  ←─────────────────────────→ Don't wait for confirm
        │
        retries=1,  ←──────────────────────→ Retry once if failed
        │
        max_block_ms=5000,  ←──────────────→ Wait max 5 seconds
        │
        request_timeout_ms=5000,  ←────────→ Timeout after 5 seconds
        │
        linger_ms=1000,  ←─────────────────→ Batch messages for 1 sec
        │
        batch_size=16384  ←────────────────→ Batch up to 16KB
    )

    Result: Producer object ready to send messages
```

---

## 📤 Message Send Process

```
┌─────────────────────────────────────────────────────────────────┐
│              KAFKA SEND DETAILED FLOW                            │
└─────────────────────────────────────────────────────────────────┘

Step 1: Item arrives at pipeline
    │
    ▼
    def process_item(self, item, spider):
        item_dict = dict(item)
    
    ┌─────────────────────────────┐
    │ item_dict = {                │
    │   'flight_number': 'AI303',  │
    │   'airline': 'Air India',    │
    │   ...                        │
    │ }                            │
    └─────────────────────────────┘

Step 2: Call producer.send()
    │
    ▼
    self.producer.send('flight-data', item_dict)
                       │            │
                       │            └─→ DATA (Python dict)
                       │
                       └─→ TOPIC NAME (string)

Step 3: Kafka library processes
    │
    ├─→ Serializes data (dict → JSON → bytes)
    │
    ├─→ Creates Kafka message
    │   ┌────────────────────────┐
    │   │ Key: None              │
    │   │ Value: <bytes>         │
    │   │ Topic: 'flight-data'   │
    │   │ Partition: 0 (default) │
    │   └────────────────────────┘
    │
    └─→ Adds to send buffer

Step 4: Network transmission
    │
    ├─→ Batches messages (if linger_ms > 0)
    │
    ├─→ Sends TCP packet to 10.7.6.33:9092
    │
    └─→ acks=0 means "don't wait for response"

Step 5: Kafka broker receives
    │
    ├─→ Writes to 'flight-data' topic log
    │
    ├─→ Assigns offset number
    │
    └─→ Data is now available for consumers

Step 6: Return to pipeline
    │
    └─→ Continue processing next item
```

---

## 🗂️ File Interaction Map

```
┌────────────────────────────────────────────────────────────────┐
│                    FILE DEPENDENCIES                            │
└────────────────────────────────────────────────────────────────┘

settings.py
    │
    │ imports/references
    ▼
kafka_pipeline.py
    │
    │ from kafka import KafkaProducer
    ▼
kafka-python library
    │
    │ network connection
    ▼
VM Kafka Broker (10.7.6.33:9092)


simple_flight_spider.py
    │
    │ uses data model from
    ▼
items.py (FlightItem)
    │
    │ yields to
    ▼
Scrapy Engine
    │
    │ passes to
    ▼
kafka_pipeline.py (process_item)
    │
    │ sends via
    ▼
KafkaProducer
    │
    │ transmits to
    ▼
VM Kafka


flight_generator.py
    │
    │ imports
    ▼
kafka_pipeline.py
    │
    │ reuses
    ▼
Same Kafka connection logic
```

---

## 📊 Data Size Through Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│                DATA SIZE AT EACH STAGE                          │
└────────────────────────────────────────────────────────────────┘

Stage 1: Python Object (in memory)
    FlightItem object
    Size: ~500 bytes (object overhead)

Stage 2: Python Dictionary (in memory)
    {'flight_number': 'AI303', ...}
    Size: ~300 bytes

Stage 3: JSON String (in memory)
    '{"flight_number":"AI303",...}'
    Size: ~250 bytes

Stage 4: UTF-8 Bytes (in memory)
    b'{"flight_number":"AI303",...}'
    Size: ~250 bytes

Stage 5: Kafka Message (network packet)
    [Headers][Key][Value]
    Size: ~300 bytes (with Kafka overhead)

Stage 6: Kafka Log (disk on VM)
    Compressed and stored
    Size: ~200 bytes (with compression)
```

---

## 🎯 Key Configuration Points Visual

```
┌────────────────────────────────────────────────────────────────┐
│           CRITICAL CONFIGURATION LOCATIONS                      │
└────────────────────────────────────────────────────────────────┘

1. VM IP ADDRESS
   ┌─────────────────────────────────────┐
   │ kafka_pipeline.py                   │
   │ Line 19:                            │
   │ bootstrap_servers=['10.7.6.33:9092']│ ← CHANGE HERE
   └─────────────────────────────────────┘

2. KAFKA TOPIC NAME
   ┌─────────────────────────────────────┐
   │ kafka_pipeline.py                   │
   │ Line 48:                            │
   │ producer.send('flight-data', data)  │ ← CHANGE HERE
   └─────────────────────────────────────┘

3. PIPELINE ACTIVATION
   ┌─────────────────────────────────────┐
   │ settings.py                         │
   │ Line 12:                            │
   │ ITEM_PIPELINES = {                  │
   │   'kafka_pipeline.KafkaPipeline': 300 ← ENABLE HERE
   │ }                                   │
   └─────────────────────────────────────┘

4. DATA MODEL
   ┌─────────────────────────────────────┐
   │ items.py                            │
   │ Line 4-16:                          │
   │ class FlightItem(scrapy.Item):      │
   │   flight_number = scrapy.Field()    │ ← DEFINE FIELDS HERE
   │   airline = scrapy.Field()          │
   │   ...                               │
   └─────────────────────────────────────┘
```

---

## 🔄 Real-Time Flow Animation (Text)

```
TIME: T+0s    [Spider starts]
              └─→ Connect to Kafka... 

TIME: T+2s    [Kafka connected] ✅
              └─→ Start scraping...

TIME: T+3s    [Item 1 scraped]
              └─→ AI303: Delhi → Mumbai
              └─→ Sending to Kafka...
              └─→ Sent! ✅

TIME: T+5s    [Item 2 scraped]
              └─→ 6E205: Bangalore → Chennai
              └─→ Sending to Kafka...
              └─→ Sent! ✅

TIME: T+7s    [Item 3 scraped]
              └─→ SG442: Pune → Goa
              └─→ Sending to Kafka...
              └─→ Sent! ✅

TIME: T+8s    [Spider finished]
              └─→ Closing Kafka connection...
              └─→ Total items sent: 3 ✅
              └─→ Done!

[On VM]
TIME: T+3s    Received: AI303: Delhi → Mumbai
TIME: T+5s    Received: 6E205: Bangalore → Chennai
TIME: T+7s    Received: SG442: Pune → Goa
```

---

## 📋 Summary Diagram

```
╔═══════════════════════════════════════════════════════════════╗
║                 VOYATRA DATA FLOW SUMMARY                     ║
╚═══════════════════════════════════════════════════════════════╝

WHERE DATA COMES FROM:
    Spiders (simple_flight_spider.py, etc.)
        ↓

WHAT DATA LOOKS LIKE:
    FlightItem defined in items.py
        ↓

HOW PIPELINE ACTIVATES:
    settings.py → ITEM_PIPELINES = {kafka_pipeline: 300}
        ↓

WHERE KAFKA CONNECTION HAPPENS:
    kafka_pipeline.py → KafkaProducer(10.7.6.33:9092)
        ↓

HOW DATA TRANSFERS:
    producer.send('flight-data', item_dict)
        ↓

WHERE DATA GOES:
    VM Kafka Broker → Topic: 'flight-data'
        ↓

WHO READS IT:
    Kafka Consumer on VM

KEY FILES:
    1. items.py          → Data structure
    2. *_spider.py       → Data source
    3. settings.py       → Pipeline config
    4. kafka_pipeline.py → Kafka connection (MOST IMPORTANT!)
    5. flight_generator.py → Standalone test
```

---

**Use these diagrams to explain the data flow in your presentation! Visual learners will love it! 🎨**