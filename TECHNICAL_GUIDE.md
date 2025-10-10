# 🎓 VoYatra Technical Documentation: Complete Data Flow Explained

## 📊 Overview: How Data Flows from Scraping to Kafka

```
┌─────────────────┐
│  Spider Starts  │  (simple_flight_spider.py)
└────────┬────────┘
         │ Scrapes/Generates Flight Data
         ▼
┌─────────────────┐
│  FlightItem     │  (items.py - Data Model)
│  Created        │
└────────┬────────┘
         │ Passes through Pipeline
         ▼
┌─────────────────┐
│ KafkaPipeline   │  (kafka_pipeline.py)
│ process_item()  │
└────────┬────────┘
         │ Sends to Kafka
         ▼
┌─────────────────┐
│  Kafka Broker   │  (10.7.6.33:9092)
│  Topic:         │
│  'flight-data'  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  VM Consumer    │  (Your VM)
│  Processes Data │
└─────────────────┘
```

---

## 📁 Core Files Explained (Where Data Comes From & Goes)

### 1️⃣ **items.py** - Data Structure Definition
**Location**: `scrapers/travel_scrapers/items.py`

**Purpose**: Defines what data fields each type of item will have

```python
class FlightItem(scrapy.Item):
    flight_number = scrapy.Field()    # e.g., "AI302"
    airline = scrapy.Field()           # e.g., "Air India"
    source = scrapy.Field()            # e.g., "Delhi"
    destination = scrapy.Field()       # e.g., "Mumbai"
    departure_time = scrapy.Field()    # e.g., "10:30"
    arrival_time = scrapy.Field()      # e.g., "12:45"
    price = scrapy.Field()             # e.g., 4500.0
    duration = scrapy.Field()          # e.g., "2h 15m"
    stops = scrapy.Field()             # e.g., "Non-stop"
    scraped_at = scrapy.Field()        # e.g., "2025-10-09T14:30:00"
    url = scrapy.Field()               # Source URL
```

**What it does**:
- 📋 Creates a blueprint for flight data
- ✅ Ensures all spiders use the same data format
- 🔒 Type safety - only defined fields are allowed

**Data Flow**: 
```
Spider creates FlightItem → Fills in fields → Sends to pipeline
```

---

### 2️⃣ **Spider Files** - Where Data Comes From
**Location**: `scrapers/travel_scrapers/spiders/`

#### Example: `simple_flight_spider.py`

```python
class SimpleFlightSpider(scrapy.Spider):
    name = 'simple_flight'
    
    def parse(self, response):
        # Generate 3 test flights
        for i in range(3):
            yield {
                'flight_number': 'AI303',
                'airline': 'Air India',
                'source': 'Delhi',
                'destination': 'Mumbai',
                'price': 4500.0,
                # ... more fields
            }
```

**What it does**:
- 🕷️ **Crawls** websites or generates data
- 🔍 **Extracts** flight information
- 📦 **Creates** FlightItem objects
- ⚡ **Yields** items to the Scrapy pipeline

**Data Source Options**:
1. **simple_flight** → Generates fake data (for testing)
2. **flight_spider** → Scrapes real websites (template)
3. **flights_spider_enhanced** → Advanced scraping with anti-bot
4. **amadeus_flight_spider** → API-based (recommended)

**Data Flow**:
```
Website/API → Spider.parse() → yield FlightItem → Pipeline
```

---

### 3️⃣ **settings.py** - Pipeline Configuration
**Location**: `scrapers/travel_scrapers/settings.py`

**Purpose**: Tells Scrapy which pipelines to use and in what order

```python
# THIS IS THE KEY CONNECTION!
ITEM_PIPELINES = {
    'kafka_pipeline.KafkaPipeline': 300,  # ← Activates Kafka streaming
}
```

**What this means**:
- ✅ Every item from spiders will go through `KafkaPipeline`
- 🔢 Number `300` is priority (lower runs first)
- 📡 This is WHERE the Kafka connection is activated

**Without this line**: Data would be scraped but NOT sent to Kafka!

**Data Flow**:
```
settings.py tells Scrapy → Use KafkaPipeline → For every item
```

---

### 4️⃣ **kafka_pipeline.py** - THE KAFKA CONNECTION (Most Important!)
**Location**: `scrapers/kafka_pipeline.py`

**Purpose**: This is the BRIDGE between your scraped data and Kafka

#### Step-by-Step Breakdown:

```python
class KafkaPipeline:
    def __init__(self):
        self.producer = None        # Kafka producer (not created yet)
        self.items_sent = 0         # Counter for tracking
```

#### **When Spider Starts**:
```python
def open_spider(self, spider):
    # THIS IS WHERE KAFKA CONNECTION HAPPENS!
    self.producer = KafkaProducer(
        bootstrap_servers=['10.7.6.33:9092'],  # ← YOUR VM IP:PORT
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks=0,                                 # Fire-and-forget mode
        retries=1,
        max_block_ms=5000,
        request_timeout_ms=5000,
        linger_ms=1000,
        batch_size=16384
    )
```

**What each parameter means**:
- `bootstrap_servers=['10.7.6.33:9092']` → **WHERE** to connect (your VM)
- `value_serializer` → Converts Python dict to JSON
- `acks=0` → Don't wait for confirmation (faster)
- `max_block_ms=5000` → Wait max 5 seconds
- `batch_size=16384` → Group messages for efficiency

#### **When Item is Scraped**:
```python
def process_item(self, item, spider):
    # 1. Convert Scrapy item to dictionary
    item_dict = dict(item)
    
    # 2. THIS LINE SENDS DATA TO KAFKA!
    self.producer.send('flight-data', item_dict)
    #                   ^^^^^^^^^^^^  ^^^^^^^^^^
    #                   TOPIC NAME    DATA
    
    # 3. Track sent items
    self.items_sent += 1
    
    return item
```

**This is THE KEY MOMENT**: Data is sent to Kafka!

#### **When Spider Ends**:
```python
def close_spider(self, spider):
    # Ensure all messages are sent
    self.producer.flush()
    # Close connection
    self.producer.close()
```

**Complete Data Flow Through Pipeline**:
```
Spider yields item 
    ↓
settings.py routes to KafkaPipeline
    ↓
KafkaPipeline.process_item() receives item
    ↓
Convert to dictionary
    ↓
producer.send('flight-data', data) ← KAFKA SEND HAPPENS HERE
    ↓
Data travels over network to 10.7.6.33:9092
    ↓
Kafka broker on VM receives it
    ↓
VM consumer can read from 'flight-data' topic
```

---

### 5️⃣ **pipelines.py** - Data Validation (Optional)
**Location**: `scrapers/travel_scrapers/pipelines.py`

**Purpose**: Clean and validate data before sending to Kafka

```python
class DataValidationPipeline:
    def process_item(self, item, spider):
        # Add timestamp if missing
        if not item.get('scraped_at'):
            item['scraped_at'] = datetime.now().isoformat()
        return item
```

**What it does**:
- ✅ Validates data fields
- 🕐 Adds timestamps
- 🧹 Cleans data

**Note**: Currently disabled in settings.py, but available if needed

---

### 6️⃣ **flight_generator.py** - Standalone Test Tool
**Location**: `flight_generator.py`

**Purpose**: Test Kafka pipeline WITHOUT running full Scrapy

```python
# Import the same Kafka pipeline
from kafka_pipeline import KafkaPipeline

# Create mock spider
class MockSpider:
    name = 'mock_flight_spider'
    logger = Logger()

# Use pipeline directly
pipeline = KafkaPipeline()
pipeline.open_spider(spider)
pipeline.process_item(flight_data, spider)
pipeline.close_spider(spider)
```

**What it does**:
- 🔧 Tests Kafka connection independently
- 🎯 Generates 5 sample flights
- 📤 Sends directly to Kafka
- ✅ Good for debugging

**Data Flow**:
```
flight_generator.py 
    ↓
Imports kafka_pipeline.py
    ↓
Creates sample data
    ↓
Uses same KafkaPipeline
    ↓
Sends to Kafka VM
```

---

## 🔗 How Kafka Connection Works (Technical Details)

### Connection Establishment:

```python
# 1. When spider starts
KafkaProducer(bootstrap_servers=['10.7.6.33:9092'])
    ↓
# 2. Python kafka library connects to VM
TCP Connection to 10.7.6.33 port 9092
    ↓
# 3. Handshake with Kafka broker
Kafka broker responds with metadata
    ↓
# 4. Producer is ready
Connection established ✅
```

### Data Transmission:

```python
# 1. Item scraped
yield {'flight_number': 'AI303', ...}
    ↓
# 2. Pipeline receives it
process_item(item, spider)
    ↓
# 3. Convert to JSON
json.dumps(item) → '{"flight_number": "AI303", ...}'
    ↓
# 4. Send to Kafka
producer.send('flight-data', json_data)
    ↓
# 5. Network transmission
Data packet sent to 10.7.6.33:9092
    ↓
# 6. Kafka stores it
Kafka broker writes to 'flight-data' topic
    ↓
# 7. Available for consumption
VM consumer can read it
```

---

## 🎯 Complete Example: From Scrape to Kafka

### Scenario: User runs `scrapy crawl simple_flight`

**Step 1**: Scrapy starts
```python
# settings.py is loaded
ITEM_PIPELINES = {'kafka_pipeline.KafkaPipeline': 300}
```

**Step 2**: Spider initializes
```python
# simple_flight_spider.py
spider = SimpleFlightSpider()
spider.start_requests()
```

**Step 3**: Pipeline opens
```python
# kafka_pipeline.py
pipeline.open_spider(spider)
# → Connects to 10.7.6.33:9092
# → KafkaProducer created ✅
```

**Step 4**: Spider scrapes data
```python
# simple_flight_spider.py
def parse(self, response):
    yield {
        'flight_number': 'AI303',
        'airline': 'Air India',
        'source': 'Delhi',
        'destination': 'Mumbai',
        'price': 4500.0,
        'scraped_at': '2025-10-09T14:30:00'
    }
```

**Step 5**: Item goes to pipeline
```python
# kafka_pipeline.py
def process_item(self, item, spider):
    item_dict = dict(item)  # Convert to dictionary
    
    # THIS IS THE KAFKA SEND!
    self.producer.send('flight-data', item_dict)
    #                   ^^^^^^^^^^^^
    #                   Kafka topic name
```

**Step 6**: Data sent over network
```
Windows Machine → Network → VM (10.7.6.33:9092)
```

**Step 7**: Kafka stores data
```
Kafka Broker on VM → 'flight-data' topic → Partition 0
```

**Step 8**: Consumer reads data
```python
# On your VM
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic flight-data --from-beginning

# Output:
{"flight_number":"AI303","airline":"Air India",...}
```

**Step 9**: Spider ends
```python
# kafka_pipeline.py
pipeline.close_spider(spider)
# → Flush remaining messages
# → Close Kafka connection
```

---

## 🔍 Key Configuration Points

### 1. **Kafka Broker Address**
```python
# In kafka_pipeline.py
bootstrap_servers=['10.7.6.33:9092']
#                  ^^^^^^^^^^^^^^^
#                  CHANGE THIS to your VM IP
```

### 2. **Kafka Topic Name**
```python
# In kafka_pipeline.py
self.producer.send('flight-data', item_dict)
#                  ^^^^^^^^^^^
#                  Topic where data is sent
```

### 3. **Pipeline Activation**
```python
# In settings.py
ITEM_PIPELINES = {
    'kafka_pipeline.KafkaPipeline': 300,
#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   This activates Kafka streaming
}
```

### 4. **Data Format**
```python
# In kafka_pipeline.py
value_serializer=lambda v: json.dumps(v).encode('utf-8')
#                          ^^^^^^^^^^^^
#                          Converts Python → JSON
```

---

## 📊 Data Format at Each Stage

### Stage 1: Spider Yields (Python Dict)
```python
{
    'flight_number': 'AI303',
    'airline': 'Air India',
    'source': 'Delhi',
    'destination': 'Mumbai',
    'price': 4500.0
}
```

### Stage 2: In Pipeline (Python Dict)
```python
item_dict = dict(item)
# Same as above
```

### Stage 3: Serialized for Kafka (JSON String)
```json
"{\"flight_number\":\"AI303\",\"airline\":\"Air India\",\"source\":\"Delhi\",\"destination\":\"Mumbai\",\"price\":4500.0}"
```

### Stage 4: On Kafka Broker (Bytes)
```
Binary data stored in Kafka log
```

### Stage 5: Consumer Receives (JSON String)
```json
{
  "flight_number": "AI303",
  "airline": "Air India",
  "source": "Delhi",
  "destination": "Mumbai",
  "price": 4500.0
}
```

---

## 🎓 Summary for Presentation

### **Data Origin**:
- Spiders scrape/generate flight data
- Example: `simple_flight_spider.py` creates test data

### **Data Structure**:
- Defined in `items.py` as `FlightItem`
- 11 fields: flight_number, airline, source, etc.

### **Kafka Connection**:
- `kafka_pipeline.py` is the BRIDGE
- Connects to VM: `10.7.6.33:9092`
- Topic: `flight-data`

### **Pipeline Activation**:
- `settings.py` activates pipeline
- `ITEM_PIPELINES = {'kafka_pipeline.KafkaPipeline': 300}`

### **Data Transfer**:
1. Spider yields data
2. Pipeline receives it
3. Converts to JSON
4. Sends to Kafka via `producer.send()`
5. Kafka stores it
6. VM consumer reads it

### **Key Files**:
1. `items.py` → Data model
2. `*_spider.py` → Data source
3. `settings.py` → Pipeline config
4. `kafka_pipeline.py` → Kafka connection
5. `flight_generator.py` → Standalone test

---

## 🚀 Quick Commands for Presentation

```bash
# Show spider list
cd d:\VoYatra\data-ingestion\scrapers
scrapy list

# Run with Kafka streaming
scrapy crawl simple_flight

# Test standalone
cd d:\VoYatra\data-ingestion
python flight_generator.py
```

---

**Everything is connected through Scrapy's pipeline architecture, with `kafka_pipeline.py` being the critical link that sends data to your VM!** 🎯