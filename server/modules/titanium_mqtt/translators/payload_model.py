from enum import Enum
from typing import Any


class MqttActions(Enum):
    READ = "read"
    CALIBRATE = "calibrateresponse"
    STATUS = "status"

class MqttPayloadModel:
    gateway: str = ""
    subtopic: str = ""
    indicator: str = ""
    action: MqttActions = MqttActions.READ
    payload: Any = {}
