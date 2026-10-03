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


class PressureUnits:
    Pa = "Pa"
    Psi = "psi"
    Bar = "bar"

    @classmethod
    def GetUnit(cls, unit):
        if unit in (cls.Pa, cls.Psi, cls.Bar):
            return unit
        return cls.Pa


class Panel:
    id = None
    name = ""
    gateway = ""
    topic = ""
    color = ""
    group_id = ""
    indicator = ""
    offset: float = None
    gain: float = None
    min_alarm: Alarm = None
    max_alarm: Alarm = None
    sensor_type = SensorTypes.Unknow
    multiplier = 1
    # Pressure only: values the raw gateway range (600..2400) is mapped to
    zero_value: float = None
    max_value: float = None
    # Pressure only: unit the mapped values are in
    pressure_unit: str = None

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
        if "panelGroupId" in obj:
            self.group_id = obj["panelGroupId"]
        else:
            self.group_id = obj["group"]

        if "offset" in obj:
            self.offset = obj["offset"]
        else:
            self.offset = 0

        if "gain" in obj:
            self.gain = obj["gain"]
        else:
            self.gain = 1

        if "minAlarm" in obj and "id" in obj["minAlarm"]:
            self.min_alarm = Alarm(obj["minAlarm"])

        if "maxAlarm" in obj and "id" in obj["maxAlarm"]:
            self.max_alarm = Alarm(obj["maxAlarm"])
        self.sensor_type = SensorTypes.GetType(obj["sensorType"])
        self.set_range(obj.get("zeroValue"), obj.get("maxValue"))
        self.set_pressure_unit(obj.get("pressureUnit"))

    def set_pressure_unit(self, unit):
        if self.sensor_type == SensorTypes.Pressure:
            self.pressure_unit = PressureUnits.GetUnit(unit)
        else:
            self.pressure_unit = None

    def set_range(self, zero_value, max_value):
        if (self.sensor_type == SensorTypes.Pressure and
                zero_value is not None and max_value is not None):
            self.zero_value = float(zero_value)
            self.max_value = float(max_value)
        else:
            self.zero_value = None
            self.max_value = None

    def get_calibration_info(self):
        return {
            "gateway": self.gateway,
            "indicator": self.indicator,
            "offset": self.offset,
            "gain": self.gain,
            "zeroValue": self.zero_value,
            "maxValue": self.max_value,
            "pressureUnit": self.pressure_unit
        }

    def get_full_name(self):
        return self.gateway + "-" + self.topic

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "gateway": self.gateway,
            "topic": self.topic,
            "color": self.color,
            "group": self.group_id,
            "gain": self.gain,
            "offset": self.offset,
            "indicator": self.indicator,
            "sensorType": self.sensor_type,
            "minAlarm": (self.min_alarm.to_json() if self.min_alarm else {}),
            "maxAlarm": (self.max_alarm.to_json() if self.max_alarm else {}),
            "multiplier": self.multiplier,
            "zeroValue": self.zero_value,
            "maxValue": self.max_value,
            "pressureUnit": self.pressure_unit
        }
