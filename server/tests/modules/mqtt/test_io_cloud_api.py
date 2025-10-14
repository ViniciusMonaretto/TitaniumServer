import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import json

# Importa a classe a ser testada
from modules.titanium_mqtt.translators.io_cloud_api import IoCloudApiTranslator


@pytest.fixture
def translator():
    """Instância limpa de IoCloudApiTranslator com mocks aplicados."""
    with patch("modules.titanium_mqtt.translators.io_cloud_api.Logger") as MockLogger, \
            patch("modules.titanium_mqtt.translators.io_cloud_api.MqttHelper") as MockHelper:
        t = IoCloudApiTranslator()
        t.logger = MockLogger()
        t._gateways_mapping = {}
        t.MqttHelper = MockHelper
        return t


def test_initialize_sets_empty_mapping(translator):
    translator._gateways_mapping = {"dummy": {"1": "sensor"}}
    translator.initialize()
    assert translator._gateways_mapping == {}


def test_is_valid_action(translator):
    # Simula MqttActions com valores 'report' e 'command'
    with patch("modules.titanium_mqtt.translators.io_cloud_api.MqttActions") as MockActions:
        MockActions.__iter__.return_value = [
            MagicMock(value="report"), MagicMock(value="command")]
        assert translator._is_valid_action("report")
        assert not translator._is_valid_action("invalid")


def test_get_type_of_sensor_valid_units(translator):
    valid_units = {
        "°C": "temperature",
        "kPa": "pressure",
        "V": "tension",
        "A": "current",
        "W": "power",
        "kW": "power",
        "%": "powerFactor",
    }
    for unit, expected in valid_units.items():
        assert translator._get_type_of_sensor({"unit": unit}) == expected


def test_get_type_of_sensor_invalid_unit_logs_error(translator):
    translator.logger.error = MagicMock()
    result = translator._get_type_of_sensor({"unit": "XYZ"})
    translator.logger.error.assert_called_once()
    assert result is None


def test_create_reading_success(translator):
    # Simula gateway mapeado
    translator._gateways_mapping = {"gw1": {"0": "temperature"}}

    with patch("modules.titanium_mqtt.translators.io_cloud_api.MqttReadingModel") as MockModel:
        mock_instance = MockModel.return_value
        with patch("modules.titanium_mqtt.translators.io_cloud_api.MqttHelper.get_topic_from_mosquitto_obj_report",
                   return_value="topic/test"):
            timestamp = datetime.now()
            reading_json = {"value": 25.0, "active": True}
            index_obj = {"current_index": 0}

            result = translator._create_reading(
                "gw1", timestamp, reading_json, index_obj)

            assert result == mock_instance
            assert result.value == 25.0
            assert result.is_active is True
            assert result.full_topic == "topic/test"
            assert index_obj["current_index"] == 1


def test_create_reading_missing_gateway_logs_error(translator):
    translator._gateways_mapping = {}
    translator.logger.error = MagicMock()
    index_obj = {"current_index": 0}
    result = translator._create_reading(
        "gwX", datetime.now(), {"value": 1, "active": True}, index_obj)
    translator.logger.error.assert_called_once()
    assert result is None


def test_create_calibration_update_success(translator):
    translator._gateways_mapping = {"gw1": {"0": "temperature"}}
    calibration_json = {"command_status": 0,
                        "sensor_id": 0, "gain": 1.23, "offset": 0.45}

    with patch("modules.titanium_mqtt.translators.io_cloud_api.MqttCallibrationModel") as MockModel:
        mock_instance = MockModel.return_value
        with patch("modules.titanium_mqtt.translators.io_cloud_api.MqttHelper.get_topic_from_mosquitto_obj_calibration",
                   return_value="topic/calib"):
            result = translator._create_calibration_update(
                "gw1", calibration_json)

            assert result == mock_instance
            assert result.gain == 1.23
            assert result.offset == 0.45
            assert result.full_topic == "topic/calib"


def test_create_calibration_update_failed_status_logs_error(translator):
    calibration_json = {"command_status": 1, "sensor_id": 0}
    translator.logger.error = MagicMock()
    result = translator._create_calibration_update("gw1", calibration_json)
    translator.logger.error.assert_called_once()
    assert result is None


def test_read_sensor_report_message_returns_empty_on_invalid_timestamp(translator):
    translator.logger.error = MagicMock()
    result = translator._read_sensor_report_message(
        "gw1", {"timestamp": 0, "sensors": []})
    assert result == []
    translator.logger.error.assert_called_once()


def test_read_sensor_report_message_reads_valid_data(translator):
    translator._gateways_mapping = {"gw1": {"0": "temperature"}}
    message_json = {"timestamp": 1000000000,
                    "sensors": [{"value": 10, "active": True}]}

    with patch.object(translator, "_create_reading", return_value="mockReading"):
        result = translator._read_sensor_report_message("gw1", message_json)
        assert result == ["mockReading"]


def test_translate_incoming_message_report(monkeypatch, translator):
    # Simula enums
    class FakeActions:
        REPORT = type("A", (), {"value": "report"})
        COMMAND = type("A", (), {"value": "command"})

    monkeypatch.setattr(
        "modules.titanium_mqtt.translators.io_cloud_api.MqttActions", FakeActions)
    monkeypatch.setattr(translator, "_is_valid_action", lambda x: True)
    monkeypatch.setattr(
        translator, "_read_sensor_report_message", lambda g, j: ["ok"])

    payload = json.dumps(
        {"timestamp": 1000000000, "sensors": []}).encode("utf-8")
    result = translator.translate_incoming_message(
        "iocloud/response/gw1/sensor/report", payload)

    assert result.gateway == "gw1"
    assert result.action == "report"
    assert result.data == ["ok"]
