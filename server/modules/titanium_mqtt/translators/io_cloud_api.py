from modules.titanium_mqtt.translators.translator_model import PayloadTranslator
from modules.titanium_mqtt.translators.payload_model import MqttActions, MqttPayloadModel
from support.logger import Logger
import json

class IoCloudApiTranslator(PayloadTranslator):
    logger = Logger()
    def initialize(self):
        pass

    def _is_valid_action(self, value: str) -> bool:
        return value in (action.value for action in MqttActions)

    def translate_incoming_message(self, topic: str, payload):
        
        out_payload = MqttPayloadModel()

        msg_split = topic.split('/')

        if not len(msg_split) == 5:
            self.logger.error(f"IoCloudApiTranslator::translate_payload: mqtt topic {topic} not valid")
            return None
        
        out_payload.gateway = msg_split[1]
        if not self._is_valid_action(msg_split[2]):
            self.logger.error(f"IoCloudApiTranslator::translate_payload: mqtt action {msg_split[1]} from {topic} not valid")
            return None
        
        out_payload.action = msg_split[2]
        out_payload.subtopic = msg_split[3]
        out_payload.indicator = msg_split[4]

        decoded_message = payload.decode('utf-8')
        out_payload.payload = json.loads(decoded_message)
        return out_payload
        





