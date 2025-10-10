# VM Kafka Configuration Fix

## THE PROBLEM
Your Kafka broker is advertising itself as `0.0.0.0:9092` instead of `10.7.6.33:9092`.
This prevents Windows from sending messages to Kafka.

## THE SOLUTION
You need to SSH into your VM and fix the Kafka server configuration.

## Steps to Fix (Run these on your VM):

### 1. SSH into VM
```bash
ssh cloudera@10.7.6.33
```

### 2. Find Kafka server.properties file
```bash
cd /home/cloudera/kafka_2.11-0.10.1.0/config
```

### 3. Backup the original config
```bash
cp server.properties server.properties.backup
```

### 4. Edit server.properties
```bash
nano server.properties
```

### 5. Find and modify these lines:

**FIND:**
```
#advertised.listeners=PLAINTEXT://your.host.name:9092
```

**CHANGE TO:**
```
advertised.listeners=PLAINTEXT://10.7.6.33:9092
```

**ALSO ADD (if not present):**
```
listeners=PLAINTEXT://0.0.0.0:9092
```

### 6. Save and exit (Ctrl+X, then Y, then Enter)

### 7. Restart Kafka
```bash
# Stop Kafka
cd /home/cloudera/kafka_2.11-0.10.1.0
bin/kafka-server-stop.sh

# Wait 5 seconds
sleep 5

# Start Kafka again
bin/kafka-server-start.sh -daemon config/server.properties
```

### 8. Verify Kafka is running
```bash
jps | grep Kafka
```

You should see a process ID with "Kafka"

## After Fix - Test from Windows

Run this command in PowerShell on Windows:
```powershell
cd d:\VoYatra\data-ingestion\scrapers
python run_spider.py
```

You should now see:
```
✅ Connected to Kafka on VM (10.7.6.33:9092)
✅ Sent to Kafka: AI359 (Delhi → Mumbai)
✅ Sent to Kafka: AI897 (Delhi → Mumbai)
✅ Sent to Kafka: AI283 (Delhi → Mumbai)
✅ Kafka connection closed. Total items sent: 3
```

## Verify Data on VM

Check if messages arrived:
```bash
cd /home/cloudera/kafka_2.11-0.10.1.0
bin/kafka-console-consumer.sh --zookeeper localhost:2181 --topic flight-data --from-beginning
```

You should see the flight JSON data!
