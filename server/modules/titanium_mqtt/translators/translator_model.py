from modules.titanium_mqtt.translators.payload_model import MqttPayloadModel


class PayloadTranslator:
    def initialize(self):
        pass
    
    def translate_incoming_message(self, topic, payload) -> MqttPayloadModel: 
        pass
