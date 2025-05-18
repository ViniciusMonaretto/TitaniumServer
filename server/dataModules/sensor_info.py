from datetime import datetime


class SensorInfo:
    _sensor_full_topic = ""
    _timestamp = 0
    _value = 0

    def __init__(self, 
                 sensor_full_topic: str,
                 timestamp: datetime,
                 value: int):
        self._sensor_full_topic = sensor_full_topic
        self._timestamp = timestamp.isoformat()
        self._value = value
    
    def to_json(self):
        return {
            "SensorFullTopic": self._sensor_full_topic,
            "Timestamp": self._timestamp.timestamp(),
            "Value": self._value
        }