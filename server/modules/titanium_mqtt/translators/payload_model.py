import datetime
from enum import Enum
import json
from typing import Any


class MqttActions(Enum):
    REPORT = "report"
    CALIBRATE = "calibrateresponse"
    STATUS = "status"

class MqttReadingModel:
    full_topic: str = "" 
    value: Any
    timestamp: datetime.date

    def to_dict(self):
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "subStatusName": self.full_topic
        }

class MqttPayloadModel:
    gateway: str = ""
    data: list[MqttReadingModel] = []
    action: MqttActions = MqttActions.REPORT
