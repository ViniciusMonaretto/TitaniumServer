import paho.mqtt.client as mqtt
import concurrent.futures
import random
import time
import json
import string

from datetime import datetime

def generate_random_device_id():

    hex_chars = string.hexdigits.upper() 
    random_string = ''.join(random.choice(hex_chars) for _ in range(len("1C692031BE06")))
    
    return random_string

def publish_message(client_id):
    """
    Connects to the MQTT broker and publishes a JSON message to the specified topic.

    Args:
        client_id (str): The unique client identifier used for creating the MQTT client.
    """
    client = mqtt.Client()
    client.connect(broker_address, port)
    
    message = {
        "value": round(random.uniform(22.0, 23.5), 2),
        "timestamp": datetime.now().isoformat(),
    }
    
    client.publish(topic.replace("device_id", generate_random_device_id()), json.dumps(message))  
    client.disconnect()

def stress_test_publish(num_messages):
    """
    Publishes a specified number of messages concurrently using threads.

    Args:
        num_messages (int): The number of simultaneous messages to publish.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_messages) as executor:
        futures = [executor.submit(publish_message, f"client_{i}") for i in range(num_messages)]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    broker_address = "mqtt.eclipseprojects.io"
    port = 1883
    topic = "/titanium/device_id/temperature/response"
    num_messages = 120
    for i in range(10):
        start_time = time.time()
        print(f"Starting to publish {num_messages} JSON messages concurrently...")

        stress_test_publish(num_messages)

        end_time = time.time()
        print(f"Completed publishing {num_messages} messages in {end_time - start_time:.2f} seconds.")
        print((i+1)*num_messages)
        time.sleep(10)