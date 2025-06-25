import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt

# Define the broker and port
BROKER = "mqtt.eclipseprojects.io"
PORT = 1883
MESSAGES_TO_SEND = 20

# Callback for successful connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
        # Subscribe to the command topic
        client.subscribe("iocloudcommand/#")
    else:
        print(f"Connection failed with code {rc}")

# Callback for receiving messages
def on_message(client, userdata, msg):
    print(f"Received command on topic: {msg.topic}")
    response_topic = msg.topic.replace("iocloudcommand/", "iocloud/", 1)
    response_topic = response_topic.replace("request/", "response/", 1)
    
    client.publish(response_topic, msg.payload)
    print(f"Responded to topic: {response_topic}")

# Create an MQTT client instance
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect and start the loop
client.connect(BROKER, PORT)
client.loop_start()

try:
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Sending MQTT messages")
        for i in range(MESSAGES_TO_SEND):
            topic = f"iocloud/1C692031BE04/status/temperature/{i}"
            payload = {
                "value": round(random.uniform(22.0, 22.5), 2),
                "timestamp": timestamp
            }
            payload_json = json.dumps(payload)
            client.publish(topic, payload_json)
        print("Sent MQTT messages")
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopping the client.")
    client.loop_stop()
    client.disconnect()
