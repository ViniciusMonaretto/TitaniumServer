from abc import ABC, abstractmethod
import datetime
from enum import Enum
from typing import Any


class MqttActions(Enum):
    REPORT = "report"
    COMMAND = "command"
    STATUS = "status"
    SYSTEM = "system"


class MqttDataModel(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str:Any]:
        pass


class MqttSensorStatusModel(MqttDataModel):
    status: str
    gain: float
    offset: float
    topic: str
    indicator: str
    gateway: str

    def to_dict(self):
        return {
            "status": self.status,
            "gain": self.gain,
            "offset": self.offset,
            "topic": self.topic,
            "indicator": self.indicator,
            "gateway": self.gateway
        }


class MqttErrorModel(MqttDataModel):
    full_topic: str
    gateway: str
    message: str

    def to_dict(self):
        return {
            "full_topic": self.full_topic,
            "gateway": self.gateway,
            "message": self.message
        }

class MqttGatewayModel(MqttDataModel):
    full_topic: str = ""
    name: str
    ip: str
    uptime: int

    def to_dict(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "uptime": self.uptime
        }


class MqttSystemModel(MqttDataModel):
    gateway: MqttGatewayModel
    panels: list[MqttSensorStatusModel]

    def to_dict(self):
        return {
            "gateway": self.gateway.to_dict(),
            "panels": [panel.to_dict() for panel in self.panels]
        }


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

class MqttGatewayReadingModel(MqttDataModel):
    full_topic: str = ""
    readings: list[MqttReadingModel] = []

    def __init__(self):
        self.readings = []
        self.full_topic = ""

    def to_dict(self):
        return {
            "readings": [reading.to_dict() for reading in self.readings]
        }


class MqttPayloadModel:
    gateway: str = ""
    data: list[MqttDataModel] = []
    action: MqttActions = MqttActions.REPORT
