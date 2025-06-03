class AlarmType:
    Higher = 0
    Lower = 1
    Equal = 2

class Alarm:
    _id = "" 
    _topic = ""
    _threshold = 0
    _type = AlarmType.Higher
    _panel_id = 0,

    def __init__(self, obj):
        if "id" in obj:
            self._id = obj["id"]
        self._name = obj["name"]
        self._topic = obj["topic"]
        self._threshold = obj["threshold"]
        self._type = obj["type"]
        self._panel_id = obj["panelId"]
    
    def to_json(self):
        return {
            "id": self._id,
            "name": self._name,
            "topic": self._topic,
            "threshold": self._threshold,
            "type": self._type,
            "panelId": self._panel_id
        }