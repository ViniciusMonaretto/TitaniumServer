import uuid

class SensorTypes:
    Pressure = "Pressure"
    Temperature = "Temperature"
    Power = "Power"
    Unknow = "Unknow"

    @classmethod
    def GetType(cls, panelName):
        if panelName == cls.Pressure:
            return cls.Pressure
        elif panelName == cls.Temperature:
            return cls.Temperature
        elif panelName == cls.Power:
            return cls.Power
        
        return cls.Unknow

class Panel:
    _id = None
    _name = ""
    _gateway = ""
    _topic = ""
    _color = ""
    _group = ""
    _sensor_type = SensorTypes.Unknow
    def __init__(self, obj):
        if "id" in obj:
            self._id = obj["id"]
        self._name = obj["name"]
        self._gateway = obj["gateway"]
        self._topic = obj["topic"]
        self._color = obj["color"]
        if "panelGroup" in obj:
            self._group = obj["panelGroup"]
        else:
            self._group = obj["group"]
        self._sensor_type = SensorTypes.GetType(obj["sensorType"])
    
    def get_full_name(self):
        return self._gateway + "-" + self._topic
    
    def to_json(self):
        return {
            "id": self._id,
            "name": self._name,
            "gateway": self._gateway,
            "topic": self._topic,
            "color": self._color,
            "group": self._group,
            "sensorType": self._sensor_type,
        }