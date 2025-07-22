from datetime import datetime
from typing import Any
from modules.titanium_mqtt.translators.translator_model import PayloadTranslator
from modules.titanium_mqtt.translators.payload_model import (
    MqttActions,
    MqttCallibrationModel,
    MqttPayloadModel,
    MqttReadingModel,
)
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

    def _create_calibration_update(self, gateway, calibration_json):
        calibration_update: MqttCallibrationModel = MqttCallibrationModel()

        type_of_sensor = calibration_json["type"]
        index = calibration_json["sensor_id"]
        calibration_update.full_topic = (
            MqttHelper.get_topic_from_mosquitto_obj_calibration(
                gateway, type_of_sensor, str(index)
            )
        )

        calibration_update.gain = calibration_json["gain"]
        calibration_update.offset = calibration_json["offset"]

        return calibration_update

    def _create_reading(self, gateway, timestamp, reading_json, index_obj):
        reading: MqttReadingModel = MqttReadingModel()
        type_of_sensor = ""

        if reading_json["unit"] not in index_obj:
            index_obj[reading_json["unit"]] = 0

        index = index_obj[reading_json["unit"]]
        index_obj[reading_json["unit"]] += 1

        if reading_json["unit"] == "°C":
            type_of_sensor = "temperature"
        elif reading_json["unit"] == "kPa":
            type_of_sensor = "pressure"
        else:
            self.logger.error(
                f"IoCloudApiTranslator::_create_reading: mqtt unit not recognized {reading_json['unit']}"
            )
            return None

        reading.full_topic = MqttHelper.get_topic_from_mosquitto_obj_report(
            gateway, type_of_sensor, str(index)
        )

        reading.value = reading_json["value"]
        reading.timestamp = timestamp

        return reading

    def _read_sensor_report_message(self, gateway: str, message_json: Any):
        timestamp = datetime.fromisoformat(message_json["timestamp"])
        data = []
        index_obj = {}
        for raw_reading in message_json["sensors"]:
            reading = self._create_reading(gateway, timestamp, raw_reading, index_obj)
            if reading:
                data.append(reading)

        return data

    def _read_calibration_update_message(self, gateway: str, message_json: Any):
        return [self._create_calibration_update(gateway, message_json)]

    def translate_incoming_message(self, topic: str, payload):
        out_payload = MqttPayloadModel()

        msg_split = topic.split("/")
        out_payload.gateway = msg_split[2]
        action_str = msg_split[-1]

        if not self._is_valid_action(action_str):
            self.logger.error(
                f"IoCloudApiTranslator::translate_payload: mqtt action {action_str} from {topic} not valid"
            )
            return None

        out_payload.action = action_str
        decoded_message = payload.decode("utf-8")
        message_json = json.loads(decoded_message)

        if action_str == MqttActions.REPORT.value:
            if not len(msg_split) == 5:
                self.logger.error(
                    f"IoCloudApiTranslator::translate_payload: mqtt topic {topic} not valid"
                )
            out_payload.data = self._read_sensor_report_message(
                msg_split[2], message_json
            )
        elif action_str == MqttActions.COMMAND.value:
            if not len(msg_split) == 4:
                self.logger.error(
                    f"IoCloudApiTranslator::translate_payload: mqtt topic {topic} not valid"
                )

            if message_json["command"] == 1:
                out_payload.data = self._read_calibration_update_message(
                    msg_split[2], message_json["params"]
                )

        return out_payload
