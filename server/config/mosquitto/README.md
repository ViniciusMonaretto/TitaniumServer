# Mosquitto MQTT Server

This directory contains the configuration for the Mosquitto MQTT broker used by the Titanium Server.

## Configuration

The MQTT server is configured via `config/mosquitto.conf` with the following settings:

- **Port 1883**: Standard MQTT protocol
- **Port 9001**: MQTT over WebSocket (for web applications)
- **Anonymous connections**: Enabled for development
- **Persistence**: Enabled to maintain message history
- **Logging**: Enabled with timestamps

## Usage

### Starting the Services

To start both MongoDB and Mosquitto:

```bash
cd server
docker-compose up -d
```

### Connecting to MQTT

#### Standard MQTT Client
- **Host**: localhost
- **Port**: 1883
- **Protocol**: MQTT

#### WebSocket MQTT Client
- **Host**: localhost
- **Port**: 9001
- **Protocol**: WebSocket

### Testing the MQTT Server

You can test the MQTT server using any MQTT client. Here are some examples:

#### Using mosquitto_pub and mosquitto_sub (command line)

```bash
# Subscribe to a topic
mosquitto_sub -h localhost -p 1883 -t "test/topic"

# Publish to a topic
mosquitto_pub -h localhost -p 1883 -t "test/topic" -m "Hello MQTT!"
```

#### Using Python with paho-mqtt

```python
import paho.mqtt.client as mqtt

# Create client
client = mqtt.Client()

# Connect to broker
client.connect("localhost", 1883, 60)

# Publish message
client.publish("test/topic", "Hello from Python!")

# Subscribe to topic
client.subscribe("test/topic")

# Start loop
client.loop_forever()
```

## Security Considerations

For production deployment, consider:

1. **Authentication**: Uncomment and configure `password_file` in mosquitto.conf
2. **Access Control**: Uncomment and configure `acl_file` in mosquitto.conf
3. **TLS/SSL**: Add SSL certificates and configure secure connections
4. **Network Security**: Restrict access to MQTT ports

## Volumes

The docker-compose creates three volumes:
- `mosquitto_data`: Persistent MQTT data
- `mosquitto_logs`: MQTT log files
- `mongo_data`: MongoDB data

## Troubleshooting

### Check MQTT Server Status
```bash
docker-compose ps
```

### View MQTT Logs
```bash
docker-compose logs mosquitto
```

### Restart MQTT Server
```bash
docker-compose restart mosquitto
```

### Access MQTT Container Shell
```bash
docker-compose exec mosquitto sh
``` 
