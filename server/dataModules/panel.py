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
    id = None
    name = ""
    gateway = ""
    topic = ""
    color = ""
    group = ""
    indicator = ""
    sensor_type = SensorTypes.Unknow
    def __init__(self, obj):
        if "id" in obj:
            self.id = obj["id"]
        self.name = obj["name"]
        self.gateway = obj["gateway"]
        self.topic = obj["topic"]
        self.color = obj["color"]
        self.indicator = obj["indicator"]
        if "panelGroup" in obj:
            self.group = obj["panelGroup"]
        else:
            self.group = obj["group"]
        self.sensor_type = SensorTypes.GetType(obj["sensorType"])
    
    def get_full_name(self):
        return self.gateway + "-" + self.topic
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "gateway": self.gateway,
            "topic": self.topic,
            "color": self.color,
            "group": self.group,
            "indicator": self.indicator,
            "sensorType": self.sensor_type,
        }
