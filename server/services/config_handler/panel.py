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
    _id = 0
    _name = ""
    _gateway = ""
    _topic = ""
    _color = ""
    _sensor_type = SensorTypes.Unknow
    def __init__(self, obj):
        if("id" in obj):
            self._id = obj["id"]
        else:
            self._id = str(uuid.uuid4())
        self._name = obj["name"]
        self._gateway = obj["gateway"]
        self._topic = obj["topic"]
        self._color = obj["color"]
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
            "sensorType": self._sensor_type,
        }