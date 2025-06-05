from datetime import datetime

class EventModel:
    _id = "" 
    _alarm_id = -1
    _value = 0
    _panel_id = -1
    _timestamp: datetime = 0

    def __init__(self, alarm_id: int, panel_id: int, timestamp: datetime, value: int,  id = -1):
        self._id = id
        self._alarm_id = alarm_id
        self._panel_id = panel_id
        self._timestamp = timestamp
        self._value = value
    
    def to_json(self):
        return {
            "id": self._id,
            "alarmId": self._alarm_id,
            "panelId": self._panel_id,
            "timestamp": self._timestamp,
            "value": self._value
        }