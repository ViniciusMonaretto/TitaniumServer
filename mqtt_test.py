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

MESSAGES_TO_SEND = 20

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
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # ISO 8601 UTC format
        print("sending mqtt messages")
        for i in range(MESSAGES_TO_SEND):
            # print(f"Sending message /titanium/1C692031BE{(i + 4):02}/temperature/response")
            # Generate a random temperature value
            temperature = round(random.uniform(20.0, 30.0), 2)  # Random float between 20.0 and 30.0
            topic = f"/titanium/1C692031BE{(i + 4):02}/temperature/response"
            # Create a JSON payload
            payload = {
                "value":   round(random.uniform(22.0, 22.5), 2),
                "timestamp": timestamp
            }
            payload_json = json.dumps(payload)
            client.publish(topic, payload_json)
        print("sent mqtt messages")
        time.sleep(30)  # Wait for 5 seconds before sending the next message
except KeyboardInterrupt:
    print("Stopping the client.")
    client.loop_stop()  # Stop the loop
    client.disconnect()  # Disconnect from the broker