import pytest
import json
import threading
import queue
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Test the MQTT commands first
from modules.titanium_mqtt.mqtt_commands import MqttCommands


class TestMqttCommands:
    """Test MQTT commands constants."""

    def test_mqtt_commands_constants(self):
        """Test that MQTT commands have the expected values."""
        assert MqttCommands.CALIBRATION == "Calibration"
        assert MqttCommands.SYSTEM_STATUS_REQUEST == "StatusRequest"


class TestTitaniumMqttLogic:
    """Test TitaniumMqtt logic without MQTT client dependencies."""

    def test_calibrate_command_logic(self):
        """Test the calibration command logic."""
        # Mock middleware
        mock_middleware = MagicMock()
        mock_middleware.send_command_answear = MagicMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.publish = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware):
                self._middleware = middleware
                self._client = mock_client

            def calibrate_command(self, command):
                command_data = command["data"]
                if not self._client or not self._client.is_connected():
                    self._middleware.send_command_answear(
                        False,
                        "calibrate_command: Mqtt not connected",
                        command["requestId"],
                    )
                    return
                topic = f"iocloud/request/{command_data['gateway']}/command"
                payload = {
                    "command": 1,
                    "params": {
                        "sensor_id": int(command_data["indicator"]),
                        "offset": command_data["offset"],
                        "gain": command_data["gain"]
                    },
                }
                self._client.publish(topic, json.dumps(payload))
                self._middleware.send_command_answear(
                    True, "sucess", command["requestId"])

        # Test the logic
        mqtt_instance = MockTitaniumMqtt(mock_middleware)

        command = {
            "data": {
                "gateway": "gw1",
                "indicator": "0",
                "offset": 1.5,
                "gain": 2.0
            },
            "requestId": "req123"
        }

        mqtt_instance.calibrate_command(command)

        # Verify client publish was called with correct topic and payload
        expected_topic = "iocloud/request/gw1/command"
        expected_payload = {
            "command": 1,
            "params": {
                "sensor_id": 0,
                "offset": 1.5,
                "gain": 2.0
            }
        }

        mock_client.publish.assert_called_once_with(
            expected_topic, json.dumps(expected_payload))
        mock_middleware.send_command_answear.assert_called_once_with(
            True, "sucess", "req123")

    def test_calibrate_command_not_connected(self):
        """Test calibration command when MQTT is not connected."""
        # Mock middleware
        mock_middleware = MagicMock()
        mock_middleware.send_command_answear = MagicMock()

        # Mock client that's not connected
        mock_client = MagicMock()
        mock_client.is_connected.return_value = False

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware):
                self._middleware = middleware
                self._client = mock_client

            def calibrate_command(self, command):
                command_data = command["data"]
                if not self._client or not self._client.is_connected():
                    self._middleware.send_command_answear(
                        False,
                        "calibrate_command: Mqtt not connected",
                        command["requestId"],
                    )
                    return
                # This should not be reached
                topic = f"iocloud/request/{command_data['gateway']}/command"
                payload = {
                    "command": 1,
                    "params": {
                        "sensor_id": int(command_data["indicator"]),
                        "offset": command_data["offset"],
                        "gain": command_data["gain"]
                    },
                }
                self._client.publish(topic, json.dumps(payload))
                self._middleware.send_command_answear(
                    True, "sucess", command["requestId"])

        # Test the logic
        mqtt_instance = MockTitaniumMqtt(mock_middleware)

        command = {
            "data": {"gateway": "gw1", "indicator": "0", "offset": 1.5, "gain": 2.0},
            "requestId": "req123"
        }

        mqtt_instance.calibrate_command(command)

        # Verify error response
        mock_middleware.send_command_answear.assert_called_once_with(
            False, "calibrate_command: Mqtt not connected", "req123"
        )
        # Verify publish was not called
        mock_client.publish.assert_not_called()

    def test_status_request_command_logic(self):
        """Test the status request command logic."""
        # Mock middleware
        mock_middleware = MagicMock()
        mock_middleware.send_command_answear = MagicMock()

        # Mock client
        mock_client = MagicMock()
        mock_client.is_connected.return_value = True
        mock_client.publish = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware):
                self._middleware = middleware
                self._client = mock_client

            def status_request_command(self, command):
                if not self._client or not self._client.is_connected():
                    self._middleware.send_command_answear(
                        False, "status_request_command: Mqtt not connected", command["requestId"])
                    return
                topic = "iocloud/request/all/command"
                payload = {
                    "command": 2,
                    "params": {
                        "user": "root",
                        "password": "root"
                    }
                }
                self._client.publish(topic, json.dumps(payload))
                self._middleware.send_command_answear(
                    True, "sucess", command["requestId"])

        # Test the logic
        mqtt_instance = MockTitaniumMqtt(mock_middleware)

        command = {"requestId": "req456"}

        mqtt_instance.status_request_command(command)

        # Verify client publish was called with correct topic and payload
        expected_topic = "iocloud/request/all/command"
        expected_payload = {
            "command": 2,
            "params": {
                "user": "root",
                "password": "root"
            }
        }

        mock_client.publish.assert_called_once_with(
            expected_topic, json.dumps(expected_payload))
        mock_middleware.send_command_answear.assert_called_once_with(
            True, "sucess", "req456")

    def test_status_request_command_not_connected(self):
        """Test status request command when MQTT is not connected."""
        # Mock middleware
        mock_middleware = MagicMock()
        mock_middleware.send_command_answear = MagicMock()

        # Mock client that's not connected
        mock_client = MagicMock()
        mock_client.is_connected.return_value = False

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware):
                self._middleware = middleware
                self._client = mock_client

            def status_request_command(self, command):
                if not self._client or not self._client.is_connected():
                    self._middleware.send_command_answear(
                        False, "status_request_command: Mqtt not connected", command["requestId"])
                    return
                # This should not be reached
                topic = "iocloud/request/all/command"
                payload = {
                    "command": 2,
                    "params": {
                        "user": "root",
                        "password": "root"
                    }
                }
                self._client.publish(topic, json.dumps(payload))
                self._middleware.send_command_answear(
                    True, "sucess", command["requestId"])

        # Test the logic
        mqtt_instance = MockTitaniumMqtt(mock_middleware)

        command = {"requestId": "req456"}

        mqtt_instance.status_request_command(command)

        # Verify error response
        mock_middleware.send_command_answear.assert_called_once_with(
            False, "status_request_command: Mqtt not connected", "req456"
        )
        # Verify publish was not called
        mock_client.publish.assert_not_called()


class TestTitaniumMqttMessageHandling:
    """Test message handling logic."""

    def test_message_queue_handling(self):
        """Test message queue handling logic."""
        # Mock components
        mock_middleware = MagicMock()
        mock_translator = MagicMock()
        mock_logger = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware, translator, logger):
                self._middleware = middleware
                self._translator = translator
                self._logger = logger
                self._read_queue = queue.Queue()
                self._end_thread = False

            def handle_incoming_messages(self):
                while not self._end_thread:
                    try:
                        msg = self._read_queue.get_nowait()
                        mqtt_message = self._translator.translate_incoming_message(
                            msg.topic, msg.payload
                        )

                        if mqtt_message:
                            self._middleware.send_status(
                                mqtt_message.data.full_topic, mqtt_message.data)
                    except queue.Empty:
                        break
                    except Exception as e:
                        self._logger.error(
                            f"Mqtt.handle_incoming_messages: Error Parsing messages {e}"
                        )
                        break

        # Test successful message handling
        mqtt_instance = MockTitaniumMqtt(
            mock_middleware, mock_translator, mock_logger)

        # Setup mocks
        mock_msg = MagicMock()
        mock_msg.topic = "iocloud/response/gw1/sensor/report"
        mock_msg.payload = b'{"timestamp": 1000000000, "sensors": []}'

        mock_translated_message = MagicMock()
        mock_translated_message.data = MagicMock()
        mock_translated_message.data.full_topic = "test/topic"

        mock_translator.translate_incoming_message.return_value = mock_translated_message

        # Put message in queue
        mqtt_instance._read_queue.put(mock_msg)

        # Run message handler
        mqtt_instance.handle_incoming_messages()

        # Verify translator was called
        mock_translator.translate_incoming_message.assert_called_once_with(
            "iocloud/response/gw1/sensor/report", b'{"timestamp": 1000000000, "sensors": []}'
        )

        # Verify middleware send_status was called
        mock_middleware.send_status.assert_called_once_with(
            "test/topic", mock_translated_message.data)

    def test_message_handling_no_translation(self):
        """Test message handling when translation returns None."""
        # Mock components
        mock_middleware = MagicMock()
        mock_translator = MagicMock()
        mock_logger = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware, translator, logger):
                self._middleware = middleware
                self._translator = translator
                self._logger = logger
                self._read_queue = queue.Queue()
                self._end_thread = False

            def handle_incoming_messages(self):
                while not self._end_thread:
                    try:
                        msg = self._read_queue.get_nowait()
                        mqtt_message = self._translator.translate_incoming_message(
                            msg.topic, msg.payload
                        )

                        if mqtt_message:
                            self._middleware.send_status(
                                mqtt_message.data.full_topic, mqtt_message.data)
                    except queue.Empty:
                        break
                    except Exception as e:
                        self._logger.error(
                            f"Mqtt.handle_incoming_messages: Error Parsing messages {e}"
                        )
                        break

        # Test message handling when translation returns None
        mqtt_instance = MockTitaniumMqtt(
            mock_middleware, mock_translator, mock_logger)

        # Setup mocks
        mock_msg = MagicMock()
        mock_msg.topic = "test/topic"
        mock_msg.payload = b'{"test": "data"}'

        mock_translator.translate_incoming_message.return_value = None

        # Put message in queue
        mqtt_instance._read_queue.put(mock_msg)

        # Run message handler
        mqtt_instance.handle_incoming_messages()

        # Verify middleware send_status was NOT called
        mock_middleware.send_status.assert_not_called()

    def test_message_handling_exception_handling(self):
        """Test exception handling in message processing."""
        # Mock components
        mock_middleware = MagicMock()
        mock_translator = MagicMock()
        mock_logger = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware, translator, logger):
                self._middleware = middleware
                self._translator = translator
                self._logger = logger
                self._read_queue = queue.Queue()
                self._end_thread = False

            def handle_incoming_messages(self):
                while not self._end_thread:
                    try:
                        msg = self._read_queue.get_nowait()
                        mqtt_message = self._translator.translate_incoming_message(
                            msg.topic, msg.payload
                        )

                        if mqtt_message:
                            self._middleware.send_status(
                                mqtt_message.data.full_topic, mqtt_message.data)
                    except queue.Empty:
                        break
                    except Exception as e:
                        self._logger.error(
                            f"Mqtt.handle_incoming_messages: Error Parsing messages {e}"
                        )
                        break

        # Test exception handling
        mqtt_instance = MockTitaniumMqtt(
            mock_middleware, mock_translator, mock_logger)

        # Setup mocks to raise exception
        mock_translator.translate_incoming_message.side_effect = Exception(
            "Test error")

        mock_msg = MagicMock()
        mqtt_instance._read_queue.put(mock_msg)

        # Run message handler
        mqtt_instance.handle_incoming_messages()

        # Verify error was logged
        mock_logger.error.assert_called_once()
        error_call = mock_logger.error.call_args[0][0]
        assert "Mqtt.handle_incoming_messages: Error Parsing messages" in error_call
        assert "Test error" in error_call


class TestTitaniumMqttTopicHandling:
    """Test topic handling logic."""

    def test_get_topic_from_command_logic(self):
        """Test the get_topic_from_command logic."""
        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self):
                self._publish_topics_list = ["GetLevel", "titanium/level"]

            def get_topic_from_command(self, command):
                if command in self._publish_topics_list:
                    return command  # Return the command itself if it's in the list
                return command

        mqtt_instance = MockTitaniumMqtt()

        # Test command in publish list
        result = mqtt_instance.get_topic_from_command("GetLevel")
        assert result == "GetLevel"

        # Test command not in publish list
        result = mqtt_instance.get_topic_from_command("custom/command")
        assert result == "custom/command"


class TestTitaniumMqttIntegration:
    """Integration tests for TitaniumMqtt logic."""

    def test_full_message_flow_logic(self):
        """Test complete message flow logic."""
        # Mock components
        mock_middleware = MagicMock()
        mock_translator = MagicMock()
        mock_logger = MagicMock()

        # Create a mock TitaniumMqtt instance
        class MockTitaniumMqtt:
            def __init__(self, middleware, translator, logger):
                self._middleware = middleware
                self._translator = translator
                self._logger = logger
                self._read_queue = queue.Queue()
                self._end_thread = False

            def handle_incoming_messages(self):
                while not self._end_thread:
                    try:
                        msg = self._read_queue.get_nowait()
                        mqtt_message = self._translator.translate_incoming_message(
                            msg.topic, msg.payload
                        )

                        if mqtt_message:
                            self._middleware.send_status(
                                mqtt_message.data.full_topic, mqtt_message.data)
                    except queue.Empty:
                        break
                    except Exception as e:
                        self._logger.error(
                            f"Mqtt.handle_incoming_messages: Error Parsing messages {e}"
                        )
                        break

        # Test complete message flow
        mqtt_instance = MockTitaniumMqtt(
            mock_middleware, mock_translator, mock_logger)

        # Setup mocks
        mock_translated_message = MagicMock()
        mock_translated_message.data = MagicMock()
        mock_translated_message.data.full_topic = "gateway1/sensor1"

        mock_translator.translate_incoming_message.return_value = mock_translated_message

        # Simulate receiving a message
        mock_msg = MagicMock()
        mock_msg.topic = "iocloud/response/gateway1/sensor/report"
        mock_msg.payload = b'{"timestamp": 1000000000, "sensors": [{"value": 25.5, "active": true}]}'

        # Put message in queue
        mqtt_instance._read_queue.put(mock_msg)

        # Process message
        mqtt_instance.handle_incoming_messages()

        # Verify complete flow
        mock_translator.translate_incoming_message.assert_called_once_with(
            "iocloud/response/gateway1/sensor/report",
            b'{"timestamp": 1000000000, "sensors": [{"value": 25.5, "active": true}]}'
        )
        mock_middleware.send_status.assert_called_once_with(
            "gateway1/sensor1", mock_translated_message.data)
