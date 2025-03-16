import paho.mqtt.client as mqtt
import time
import random
import json
from datetime import datetime

# Define the broker and port
BROKER = "mqtt.eclipseprojects.io"
PORT = 1883
TOPIC = "/titanium/1C692031BE04/temperature/response"
TOPIC2 = "/titanium/1C692031BE05/temperature/response"
TOPIC3 = "/titanium/1C692031BE06/temperature/response"

# Callback for successful connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print(f"Connection failed with code {rc}")

# Create an MQTT client instance
client = mqtt.Client()

# Assign callback for connection
client.on_connect = on_connect

# Connect to the MQTT broker
client.connect(BROKER, PORT)

# Start the network loop in a separate thread
client.loop_start()

try:
    while True:
        # Generate a random temperature value
        temperature = round(random.uniform(20.0, 30.0), 2)  # Random float between 20.0 and 30.0
        # Get the current timestamp
        timestamp = datetime.utcnow().isoformat() + "Z"  # ISO 8601 UTC format
        # Create a JSON payload
        payload = {
            "value":   round(random.uniform(22.0, 23.5), 2),
            "timestamp": timestamp
        }
        payload_json = json.dumps(payload)
        # Publish the JSON payload to the topic
        # client.publish(TOPIC, payload_json)
        # payload = {
        #     "value":  round(random.uniform(20.0, 30.0), 2),
        #     "timestamp": timestamp
        # }
        # payload_json = json.dumps(payload)
        client.publish(TOPIC2, payload_json)
        payload = {
            "value":   round(random.uniform(22.0, 23.5), 2),
            "timestamp": timestamp
        }
        payload_json = json.dumps(payload)
        client.publish(TOPIC3, payload_json)
        print(f"Published: {payload_json} to topic {TOPIC}")
        time.sleep(10)  # Wait for 5 seconds before sending the next message
except KeyboardInterrupt:
    print("Stopping the client.")
    client.loop_stop()  # Stop the loop
    client.disconnect()  # Disconnect from the broker