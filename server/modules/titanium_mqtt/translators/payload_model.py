from abc import ABC, abstractmethod
import datetime
from enum import Enum
from typing import Any


class MqttActions(Enum):
    REPORT = "report"
    COMMAND = "command"
    STATUS = "status"


class MqttDataModel(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str:Any]:
        pass


class MqttCallibrationModel(MqttDataModel):
    full_topic: str = ""
    gain: float
    offset: float

    def to_dict(self):
        return {
            "gain": self.gain,
            "offset": self.offset,
            "subStatusName": self.full_topic,
        }


class MqttReadingModel(MqttDataModel):
    full_topic: str = ""
    value: Any
    timestamp: datetime.date
    is_active: bool

    def to_dict(self):
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "subStatusName": self.full_topic,
            "isActive": self.is_active,
        }


class MqttPayloadModel:
    gateway: str = ""
    data: list[MqttDataModel] = []
    action: MqttActions = MqttActions.REPORT
