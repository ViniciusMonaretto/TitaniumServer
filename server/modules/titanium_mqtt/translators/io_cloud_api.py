from datetime import datetime
from modules.titanium_mqtt.translators.translator_model import PayloadTranslator
from modules.titanium_mqtt.translators.payload_model import MqttActions, MqttPayloadModel, MqttReadingModel
from modules.titanium_mqtt.mqtt_helper import MqttHelper
from support.logger import Logger
import json

# topic: iocloud/response/1C69209DFC08/sensor/report
# payload: {timestamp, readings: [{value, active}]}

class IoCloudApiTranslator(PayloadTranslator):
    logger = Logger()
    def initialize(self):
        pass

    def _is_valid_action(self, value: str) -> bool:
        return value in (action.value for action in MqttActions)

    def _create_reading(self, 
                        action, 
                        gateway, 
                        timestamp, 
                        reading_json,
                        index_obj):
        reading: MqttReadingModel = MqttReadingModel()
        type_of_sensor = ""

        if reading_json["unit"] not in index_obj:
            index_obj[reading_json["unit"]] = 0
        
        index = index_obj[reading_json["unit"]]
        index_obj[reading_json["unit"]]+=1

        if reading_json["unit"] == "°C":
            type_of_sensor = "temperature"
        elif reading_json["unit"] == "kPa":
            type_of_sensor = "pressure"
        else:
            self.logger.error(f"IoCloudApiTranslator::_create_reading: mqtt unit not recognized {reading_json['unit']}")
            return None
        
        full_topic = MqttHelper.get_topic_from_mosquitto_obj(action, 
                                        gateway, 
                                        type_of_sensor, 
                                        str(index))
        if full_topic == None:
            return None
        
        reading.full_topic = full_topic
        reading.value = reading_json["value"]
        reading.timestamp = timestamp
    
        return reading

    def translate_incoming_message(self, topic: str, payload):
        index_obj = {}
        out_payload = MqttPayloadModel()

        msg_split = topic.split('/')

        if not len(msg_split) == 5:
            self.logger.error(f"IoCloudApiTranslator::translate_payload: mqtt topic {topic} not valid")
            return None
        
        out_payload.gateway = msg_split[2]
        if not self._is_valid_action(msg_split[4]):
            self.logger.error(f"IoCloudApiTranslator::translate_payload: mqtt action {msg_split[1]} from {topic} not valid")
            return None

        decoded_message = payload.decode('utf-8')
        message_json = json.loads(decoded_message)
        out_payload.action = msg_split[4]

        timestamp = datetime.fromisoformat(message_json["timestamp"])

        for raw_reading in message_json["sensors"]:
            reading = self._create_reading(out_payload.action, 
                msg_split[2], 
                timestamp, 
                raw_reading,
                index_obj)
            if reading:
                out_payload.data.append(reading)

        return out_payload
        





