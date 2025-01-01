import uuid

class SensorTypes:
    Pressure = "Pressure"
    Temperature = "Temperature"
    Unknow = "Unknow"

    @classmethod
    def GetType(cls, panelName):
        if panelName == cls.Pressure:
            return cls.Pressure
        elif panelName == cls.Temperature:
            return cls.Temperature
        
        return cls.Unknow

class Panel:
    _id = 0
    _name = ""
    _gateway = ""
    _topic = ""
    _sensor_type = SensorTypes.Unknow
    def __init__(self, obj):
        if("id" in obj):
            self._id = obj["id"]
        else:
            self._id = uuid.uuid4()
        self._name = obj["name"]
        self._gateway = obj["gateway"]
        self._topic = obj["topic"]
        self._sensor_type = SensorTypes.GetType(obj["sensorType"])