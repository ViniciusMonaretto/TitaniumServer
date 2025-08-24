import time
import random
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import copy

# Define the broker and port
BROKER = 'localhost'  # 'broker.hivemq.com'  # "mqtt.eclipseprojects.io"
PORT = 1883
MESSAGES_TO_SEND = 1

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

    obj = json.loads(msg.payload)
    obj["command_index"] = 1
    obj["command_status"] = 0
    obj["sensor_id"] = obj["params"]["sensor_id"]
    obj["gain"] = obj["params"]["gain"]
    obj["offset"] = obj["params"]["offset"]
    obj["unit"] = "°C"

    client.publish(response_topic, json.dumps(obj))
    print(f"Responded to topic: {response_topic}")


# Create an MQTT client instance
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect and start the loop
client.connect(BROKER, PORT)
client.loop_start()

client.subscribe("iocloud/request/#")

try:
    # Base sensor values
    base_sensors = [
        {"value": -41.5, "active": True, "unit": "°C"},
        {"value": -29.08, "active": True, "unit": "°C"},
        {"value": -18.41, "active": True, "unit": "°C"},
        {"value": -10.97, "active": True, "unit": "°C"},
        {"value": -0.67, "active": True, "unit": "°C"},
        {"value": 7.33, "active": True, "unit": "°C"},
        {"value": 20.88, "active": True, "unit": "°C"},
        {"value": 25.1, "active": True, "unit": "°C"},
        {"value": 28.18, "active": True, "unit": "°C"},
        {"value": 39.2, "active": True, "unit": "°C"},
        {"value": 48.3, "active": True, "unit": "°C"},
        {"value": 62.77, "active": True, "unit": "°C"},
        {"value": 68.89, "active": True, "unit": "°C"},
        {"value": 80.62, "active": True, "unit": "°C"},
        {"value": 92.21, "active": True, "unit": "°C"},
        {"value": 98.12, "active": True, "unit": "°C"},
        {"value": 111.21, "active": True, "unit": "°C"},
        {"value": 124.4, "active": True, "unit": "°C"},
        {"value": 132.87, "active": True, "unit": "°C"},
        {"value": 140.7, "active": True, "unit": "°C"},
        {"value": 20, "active": True, "unit": "kPa"},
        {"value": 20, "active": True, "unit": "kPa"},
        {"value": 221, "active": True, "unit": "V"},
        {"value": 2, "active": True, "unit": "A"},
        {"value": 0.96, "active": True, "unit": "%"}
    ]
    while True:
        sensors = []
        for sensor in base_sensors:
            if sensor["unit"] == "°C":
                varied_value = round(
                    sensor["value"] + random.uniform(-5, 5), 2)
                sensors.append({**sensor, "value": varied_value})
            else:
                sensors.append(sensor.copy())
        payload = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "sensors": sensors,
        }
        topic = "iocloud/response/1C69209DFC08/sensor/report"
        payload_json = json.dumps(payload)
        print(f"Sending MQTT message to {topic}")
        client.publish(topic, payload_json)
        print("Sent MQTT message")
        time.sleep(30)
except KeyboardInterrupt:
    print("Stopping the client.")
    client.loop_stop()
    client.disconnect()
