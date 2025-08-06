from .alarm import Alarm


class SensorTypes:
    Pressure = "Pressure"
    Temperature = "Temperature"
    Power = "Power"
    Current = "Current"
    Tension = "Tension"
    PowerFactor = "PowerFactor"
    Unknow = "Unknow"

    @classmethod
    def GetType(cls, panelName):
        if panelName == cls.Pressure:
            return cls.Pressure
        elif panelName == cls.Temperature:
            return cls.Temperature
        elif panelName == cls.Power:
            return cls.Power
        elif panelName == cls.Current:
            return cls.Current
        elif panelName == cls.Tension:
            return cls.Tension
        elif panelName == cls.PowerFactor:
            return cls.PowerFactor

        return cls.Unknow


class Panel:
    id = None
    name = ""
    gateway = ""
    topic = ""
    color = ""
    group = ""
    indicator = ""
    offset: float = None
    gain: float = None
    min_alarm: Alarm = None
    max_alarm: Alarm = None
    sensor_type = SensorTypes.Unknow
    multiplier = 1

    def __init__(self, obj):
        if "id" in obj:
            self.id = obj["id"]
        self.name = obj["name"]
        self.gateway = obj["gateway"]
        self.topic = obj["topic"]
        self.color = obj["color"]
        self.indicator = obj["indicator"]
        if "multiplier" in obj:
            self.multiplier = obj["multiplier"]
        else:
            self.multiplier = 1
        if "panelGroup" in obj:
            self.group = obj["panelGroup"]
        else:
            self.group = obj["group"]

        if "offset" in obj:
            self.offset = obj["offset"]
        if "gain" in obj:
            self.gain = obj["gain"]

        if "minAlarm" in obj and "id" in obj["minAlarm"]:
            self.min_alarm = Alarm(obj["minAlarm"])

        if "maxAlarm" in obj and "id" in obj["maxAlarm"]:
            self.max_alarm = Alarm(obj["maxAlarm"])
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
            "gain": self.gain,
            "offset": self.offset,
            "indicator": self.indicator,
            "sensorType": self.sensor_type,
            "minAlarm": (self.min_alarm.to_json() if self.min_alarm else {}),
            "maxAlarm": (self.max_alarm.to_json() if self.max_alarm else {}),
            "multiplier": self.multiplier
        }
