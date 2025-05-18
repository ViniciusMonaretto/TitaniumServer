from pymongo import MongoClient
from bson import ObjectId
import time
import math
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient("mongodb://root:example@localhost:27017/?authSource=admin")
db = client["IoCloud"]
collection = db["SensorData"]

# 🔄 Drop all existing documents
collection.delete_many({})
print("🗑️ Cleared existing documents from 'sensor_readings' collection.")

# Constants
TOTAL_DOCS = 1_000_000
BATCH_SIZE = 10_000
START_TIME = int((datetime.now() - timedelta(weeks=1)).timestamp())
END_TIME = int(time.time())
SENSOR_TOPIC = '1C692031BE04-temperature'

# Triangle wave function (0 to 1 range)
def triangle_wave(x, frequency=10):
    cycle = 1 / frequency
    x = x % cycle
    return 4 * abs(x - cycle / 2) / cycle - 1

# Value generator: triangular wave from 20 to 25
def generate_value(i):
    wave = triangle_wave(i / TOTAL_DOCS, frequency=5)
    return round(22.5 + 2.5 * wave, 2)  # Min 20, Max 25

# Timestamp increment per document
time_step = (END_TIME - START_TIME) / TOTAL_DOCS

# Generate and insert data
for batch_start in range(0, TOTAL_DOCS, BATCH_SIZE):
    batch = []
    for i in range(batch_start, batch_start + BATCH_SIZE):
        timestamp = int(START_TIME + i * time_step)
        value = generate_value(i)
        doc = {
            "SensorFullTopic": SENSOR_TOPIC,
            "Timestamp": timestamp,
            "Value": value
        }
        batch.append(doc)
    collection.insert_many(batch)
    print(f"Inserted {batch_start + BATCH_SIZE} documents...")

print("✅ All documents inserted.")
