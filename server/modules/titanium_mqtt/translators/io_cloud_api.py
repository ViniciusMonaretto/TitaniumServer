from datetime import datetime
from typing import Any
from modules.titanium_mqtt.translators.translator_model import PayloadTranslator
from modules.titanium_mqtt.translators.payload_model import (
    MqttActions,
    MqttCallibrationModel,
    MqttGatewayModel,
    MqttPayloadModel,
    MqttReadingModel,
    MqttSensorStatusModel,
    MqttSystemModel,
)
from modules.titanium_mqtt.mqtt_helper import MqttHelper
from support.logger import Logger
import json

# topic: iocloud/response/1C69209DFC08/sensor/report
# payload: {timestamp, readings: [{value, active}]}


class IoCloudApiTranslator(PayloadTranslator):
    logger = Logger()
    _gateways_mapping: dict[str, dict[str, str]]

    def initialize(self):
        self._gateways_mapping = {}

    def _is_valid_action(self, value: str) -> bool:
        return value in (action.value for action in MqttActions)

    def _create_calibration_update(self, gateway, calibration_json):
        calibration_update: MqttCallibrationModel = MqttCallibrationModel()

        if calibration_json["command_status"] != 0:
            self.logger.error(
                f"IoCloudApiTranslator::_create_calibration_update: Calibration for sensor {calibration_json['sensor_id']} failed"
            )
            return None

        type_of_sensor = self._get_type_of_sensor(calibration_json)
        if not type_of_sensor:
            return None

        index = calibration_json["sensor_id"]
        calibration_update.full_topic = (
            MqttHelper.get_topic_from_mosquitto_obj_calibration(
                gateway, type_of_sensor, str(index)
            )
        )

        calibration_update.gain = calibration_json["gain"]
        calibration_update.offset = calibration_json["offset"]

        return calibration_update

    def _get_type_of_sensor(self, reading_json):
        if reading_json["unit"] == "°C":
            type_of_sensor = "temperature"
        elif reading_json["unit"] == "kPa":
            type_of_sensor = "pressure"
        elif reading_json["unit"] == "V":
            type_of_sensor = "tension"
        elif reading_json["unit"] == "A":
            type_of_sensor = "current"
        elif reading_json["unit"] == "W":
            type_of_sensor = "power"
        elif reading_json["unit"] == "kW":
            type_of_sensor = "power"
        elif reading_json["unit"] == "%":
            type_of_sensor = "powerFactor"
        else:
            self.logger.error(
                f"IoCloudApiTranslator::_create_reading: mqtt unit not recognized {reading_json['unit']}"
            )
            return None
        return type_of_sensor

    def _create_reading(self, gateway, timestamp, reading_json, index_obj):
        reading: MqttReadingModel = MqttReadingModel()
        type_of_sensor = ""

        index = index_obj["current_index"]
        index_obj["current_index"] += 1

        index_str = str(index)

        if index_str not in self._gateways_mapping[gateway]:
            self.logger.error(
                f"IoCloudApiTranslator::_create_reading: gateway {gateway} dont have config for sensor {index_str}"
            )
            return None

        type_of_sensor = self._gateways_mapping[gateway][index_str]
        if (type_of_sensor == None):
            return None

        reading.full_topic = MqttHelper.get_topic_from_mosquitto_obj_report(
            gateway, type_of_sensor, str(index)
        )

        reading.value = reading_json["value"]
        reading.timestamp = timestamp
        reading.is_active = reading_json["active"]
        return reading

    def _read_sensor_report_message(self, gateway: str, message_json: Any):

        if message_json["timestamp"] is None or message_json["timestamp"] == 0:
            self.logger.error(
                "IoCloudApiTranslator::_read_sensor_report_message: timestamp is invalid"
            )
            return []

        timestamp = datetime.fromtimestamp(message_json["timestamp"])
        data = []
        index_obj = {"current_index": 0}

        if gateway not in self._gateways_mapping:
            self.logger.error(
                f"IoCloudApiTranslator::_read_sensor_report_message: gateway {gateway} not found in gateways mapping"
            )
            return []

        for raw_reading in message_json["sensors"]:
            reading = self._create_reading(
                gateway, timestamp, raw_reading, index_obj)
            if reading:
                data.append(reading)

        return data

    def _read_calibration_update_message(self, gateway: str, message_json: Any):
        return [self._create_calibration_update(gateway, message_json)]

    def _read_system_message(self, message_json: Any):
        return [self._create_system_update(message_json)]

    def _create_system_update(self, message_json: Any):
        system: MqttGatewayModel = MqttGatewayModel()

        system.name = message_json["device_id"]
        system.ip = message_json["ip_address"]
        system.uptime = message_json["uptime"]

        panels = []

        self._gateways_mapping[message_json["device_id"]] = {}

        for panel in message_json["sensors"]:
            system_panel: MqttSensorStatusModel = MqttSensorStatusModel()
            system_panel.status = panel["state"] == 0
            system_panel.gain = panel["gain"]
            system_panel.offset = panel["offset"]
            system_panel.topic = self._get_type_of_sensor(panel)
            self._gateways_mapping[message_json["device_id"]][str(
                panel["index"])] = system_panel.topic
            system_panel.indicator = panel["index"]
            system_panel.gateway = message_json["device_id"]
            panels.append(system_panel)

        system_module = MqttSystemModel()
        system_module.gateway = system
        system_module.panels = panels
        system_module.full_topic = "gateway-status-*"

        return system_module

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

            if message_json["command_index"] == 1:
                out_payload.data = self._read_calibration_update_message(
                    msg_split[2], message_json
                )
            elif message_json["command_index"] == 2:
                if not len(msg_split) == 4:
                    self.logger.error(
                        f"IoCloudApiTranslator::translate_payload: mqtt topic {topic} not valid"
                    )
                out_payload.data = self._read_system_message(message_json)

        return out_payload
