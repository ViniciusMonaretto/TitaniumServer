from datetime import datetime


class SensorInfo:
    sensor_full_topic = ""
    timestamp: datetime
    value = 0

    def __init__(self,
                 sensor_full_topic: str,
                 timestamp: datetime,
                 value: int):
        self.sensor_full_topic = sensor_full_topic
        self.timestamp = timestamp.isoformat()
        self.value = value

    def to_json(self):
        return {
            "SensorFullTopic": self.sensor_full_topic,
            "Timestamp": self.timestamp,
            "Value": self.value
        }
