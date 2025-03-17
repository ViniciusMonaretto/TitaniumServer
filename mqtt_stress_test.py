import paho.mqtt.client as mqtt
import threading
import time
import random
from datetime import datetime

BROKER = "mqtt.eclipseprojects.io"
PORT = 1883
TOPICS = [
    "/titanium/1C692031BE04/temperature/response",
    "/titanium/1C692031BE05/temperature/response",
    "/titanium/1C692031BE06/temperature/response"
]
NUM_CLIENTS = 10  # Number of clients to simulate
PUBLISH_INTERVAL = 0.1  # Time between publishes (seconds)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT broker as {userdata}")
        for topic in TOPICS:
            client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"{userdata} received: {msg.topic} -> {msg.payload.decode()}")

def mqtt_client_thread(client_id):
    client = mqtt.Client(client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    client.user_data_set(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    
    while True:
        timestamp = datetime.isoformat()  # ISO 8601 UTC format
        topic = random.choice(TOPICS)
        payload = {
            "value":   round(random.uniform(22.0, 23.5), 2),
            "timestamp": timestamp
        }
        client.publish(topic, payload)
        print(f"{client_id} published: {topic} -> {payload}")
        time.sleep(PUBLISH_INTERVAL)

def start_stress_test():
    threads = []
    for i in range(NUM_CLIENTS):
        client_id = f"TestClient-{i}"
        t = threading.Thread(target=mqtt_client_thread, args=(client_id,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    start_stress_test()