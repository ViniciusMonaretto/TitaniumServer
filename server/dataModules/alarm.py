class Alarm:
    _id = "" 
    _topic = ""
    _threshold = 0
    _is_upper = False
    _panel_id = 0,

    def __init__(self, obj):
        if "id" in obj:
            self._id = obj["id"]
        self._name = obj["name"]
        self._topic = obj["topic"]
        self._threshold = obj["threshold"]
        self._is_upper = obj["isUpper"]
        self._panel_id = obj["panelId"]
    
    def to_json(self):
        return {
            "id": self._id,
            "name": self._name,
            "topic": self._topic,
            "threshold": self._threshold,
            "isUpper": self._is_upper,
            "panelId": self._panel_id
        }