from datetime import datetime

class EventModel:
    event_id = "" 
    alarm_id = -1
    value = 0
    panel_id = -1
    timestamp: datetime = 0

    def __init__(self, alarm_id: int, panel_id: int, timestamp: datetime, value: int,  event_id = -1):
        self.event_id = event_id
        self.alarm_id = alarm_id
        self.panel_id = panel_id
        self.timestamp = timestamp
        self.value = value
    
    def to_json(self):
        return {
            "id": self.event_id,
            "alarmId": self.alarm_id,
            "panelId": self.panel_id,
            "timestamp": self.timestamp,
            "value": self.value
        }
