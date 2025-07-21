from support.logger import Logger
from middleware.client_middleware import ClientMiddleware
from modules.titanium_mqtt.translators.payload_model import MqttPayloadModel

class MqttHelper:
    @staticmethod
    def get_topic_from_mosquitto_obj(action, gateway, subtopic, indicator):
        if action == "calibrateresponse":
            return ClientMiddleware.get_calibrate_topic(gateway, subtopic, indicator)
        elif action == "report":
            return ClientMiddleware.get_status_topic(gateway, subtopic, indicator)
        else:
            Logger().warning(
                f"TitaniumMqtt::get_topic_from_mosquitto_obj: Mqtt message action not supported: {action}")
