from abc import ABC, abstractmethod
from typing import Any
from modules.titanium_mqtt.translators.payload_model import MqttPayloadModel


class PayloadTranslator(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def translate_incoming_message(self, topic, payload) -> MqttPayloadModel:
        pass

    @abstractmethod
    def update_calibration(self, calibration_info: list[Any]):
        pass
