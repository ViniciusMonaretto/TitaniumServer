#!/usr/bin/env python3
"""
Simple MQTT test script to verify the Mosquitto server is working.
Requires: pip install paho-mqtt
"""

import paho.mqtt.client as mqtt
import time
import json

# MQTT Configuration
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "test/titanium"


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        # Subscribe to test topic
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker, return code: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")


def on_publish(client, userdata, mid):
    """Callback when message is published"""
    print(f"Message published with ID: {mid}")


def test_mqtt_connection():
    """Test MQTT connection and basic publish/subscribe"""
    try:
        # Create MQTT client
        client = mqtt.Client()

        # Set callbacks
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_publish = on_publish

        # Connect to broker
        print(f"Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}...")
        client.connect(MQTT_HOST, MQTT_PORT, 60)

        # Start the loop in a non-blocking way
        client.loop_start()

        # Wait a moment for connection
        time.sleep(2)

        # Publish a test message
        test_message = {
            "timestamp": time.time(),
            "message": "Hello from Titanium Server MQTT test!",
            "value": 42.5
        }

        print(f"Publishing test message to topic: {MQTT_TOPIC}")
        client.publish(MQTT_TOPIC, json.dumps(test_message))

        # Wait for message to be received
        time.sleep(3)

        # Stop the loop
        client.loop_stop()
        client.disconnect()

        print("MQTT test completed successfully!")
        return True

    except Exception as e:
        print(f"MQTT test failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting MQTT connection test...")
    success = test_mqtt_connection()

    if success:
        print("✅ MQTT server is working correctly!")
    else:
        print("❌ MQTT server test failed!")
        print("\nTroubleshooting:")
        print("1. Make sure Docker containers are running: docker-compose up -d")
        print("2. Check if port 1883 is available: netstat -an | grep 1883")
        print("3. Check MQTT logs: docker-compose logs mosquitto")
