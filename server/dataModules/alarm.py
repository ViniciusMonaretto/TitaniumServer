class AlarmType:
    Higher = 0
    Lower = 1
    Equal = 2

class Alarm:
    id = "" 
    topic = ""
    name = ""
    threshold = 0
    type = AlarmType.Higher
    panel_id = 0,

    def __init__(self, obj):
        if "id" in obj:
            self.id = obj["id"]
        self.name = obj["name"]
        self.topic = obj["topic"]
        self.threshold = obj["threshold"]
        self.type = obj["type"]
        self.panel_id = obj["panelId"]
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "topic": self.topic,
            "threshold": self.threshold,
            "type": self.type,
            "panelId": self.panel_id
        }
