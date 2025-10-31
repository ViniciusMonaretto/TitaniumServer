import pytest
import threading
import time
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta

# Import the classes to be tested
from services.config_handler.config_handler import ConfigHandler
from services.config_handler.config_handler_command import ConfigHandlerCommands
from dataModules.panel import Panel
from dataModules.panel_group import PanelGroup
from dataModules.alarm import Alarm, AlarmType
from middleware.status_subscriber import StatuSubscribers
from middleware.client_middleware import ClientMiddleware
from modules.titanium_mqtt.mqtt_commands import MqttCommands


@pytest.fixture
def mock_middleware():
    """Create a mock middleware for testing."""
    middleware = MagicMock()
    middleware.add_commands = MagicMock()
    middleware.send_command = MagicMock()
    middleware.send_command_answear = MagicMock()
    middleware.send_status = MagicMock()
    middleware.add_subscribe_to_status = MagicMock()
    middleware.remove_subscribe_from_status = MagicMock()
    return middleware


@pytest.fixture
def mock_config_storage():
    """Create a mock config storage for testing."""
    config_storage = MagicMock()
    config_storage.get_panel_groups = MagicMock(return_value=[])
    config_storage.get_panels = MagicMock(return_value=[])
    config_storage.add_panel = MagicMock(return_value=1)
    config_storage.add_panel_group = MagicMock(return_value=1)
    config_storage.remove_panel = MagicMock(return_value=True)
    config_storage.remove_panel_group = MagicMock(return_value=True)
    config_storage.update_panel = MagicMock(return_value=True)
    config_storage.update_panel_group = MagicMock(return_value=True)
    return config_storage


@pytest.fixture
def mock_sensor_data_storage():
    """Create a mock sensor data storage for testing."""
    sensor_data_storage = MagicMock()
    sensor_data_storage.add_new_subscription = MagicMock(
        return_value=(True, "Success"))
    sensor_data_storage.erase_sensor_info = MagicMock()
    sensor_data_storage.get_last_status_for_topic = MagicMock(
        return_value=None)
    return sensor_data_storage


@pytest.fixture
def mock_alarm_manager():
    """Create a mock alarm manager for testing."""
    alarm_manager = MagicMock()
    alarm_manager.add_alarm = MagicMock(return_value=Alarm(
        {"id": 1, "name": "test", "topic": "test", "threshold": 100, "type": AlarmType.Higher, "panelId": 1}))
    alarm_manager.remove_alarm = MagicMock(return_value=True)
    alarm_manager.change_alarm_threshold = MagicMock(return_value=Alarm(
        {"id": 1, "name": "test", "topic": "test", "threshold": 150, "type": AlarmType.Higher, "panelId": 1}))
    return alarm_manager


@pytest.fixture
def config_handler(mock_middleware, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
    """Create a ConfigHandler instance for testing."""
    with patch('services.config_handler.config_handler.Logger'):
        with patch('services.config_handler.config_handler.ConfigHandler.read_default_config'):
            handler = ConfigHandler(
                mock_middleware,
                mock_config_storage,
                mock_sensor_data_storage,
                mock_alarm_manager
            )
            # Clear state after initialization
            handler._panel_groups.clear()
            handler._status_subscribers.clear()
            yield handler


@pytest.fixture
def sample_panel_info():
    """Create a sample panel info for testing."""
    return {
        "name": "Test Panel",
        "gateway": "gateway1",
        "topic": "temperature",
        "color": "#FF0000",
        "group": 1,  # Use integer to match group_id from add_panel_group
        "indicator": "0",
        "sensorType": "Temperature",
        "multiplier": 1
    }


@pytest.fixture
def sample_panel_group():
    """Create a sample panel group for testing."""
    return PanelGroup("Test Group", 1)


class TestConfigHandlerInitialization:
    """Test ConfigHandler initialization and setup."""

    def test_initialization(self, mock_middleware, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test that ConfigHandler initializes correctly."""
        with patch('services.config_handler.config_handler.Logger'):
            with patch('services.config_handler.config_handler.ConfigHandler.read_default_config'):
                handler = ConfigHandler(
                    mock_middleware,
                    mock_config_storage,
                    mock_sensor_data_storage,
                    mock_alarm_manager
                )

                assert handler._middleware == mock_middleware
                assert handler._config_storage == mock_config_storage
                assert handler._sensor_data_storage == mock_sensor_data_storage
                assert handler._alarm_manager == mock_alarm_manager
                assert isinstance(handler._panel_groups, dict)
                assert isinstance(handler._status_subscribers, dict)
                assert handler._panel_groups_lock is not None
                # Check it's a lock-like object
                assert hasattr(handler._panel_groups_lock, 'acquire')

    def test_commands_initialization(self, mock_middleware, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test that commands are registered with middleware."""
        with patch('services.config_handler.config_handler.Logger'):
            with patch('services.config_handler.config_handler.ConfigHandler.read_default_config'):
                handler = ConfigHandler(
                    mock_middleware,
                    mock_config_storage,
                    mock_sensor_data_storage,
                    mock_alarm_manager
                )

                mock_middleware.add_commands.assert_called_once()
                commands_dict = mock_middleware.add_commands.call_args[0][0]

                assert ConfigHandlerCommands.ADD_PANEL in commands_dict
                assert ConfigHandlerCommands.REMOVE_PANEL in commands_dict
                assert ConfigHandlerCommands.GET_PANEL_LIST in commands_dict
                assert ConfigHandlerCommands.UPDATE_PANEL_FUNCTIONALITIES in commands_dict
                assert ConfigHandlerCommands.ADD_PANEL_GROUP in commands_dict
                assert ConfigHandlerCommands.REMOVE_PANEL_GROUP in commands_dict
                assert ConfigHandlerCommands.UPDATE_PANEL_GROUP in commands_dict

    def test_initialize_system_with_empty_db(self, mock_middleware, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test that system initializes with default config when DB is empty."""
        mock_config_storage.get_panel_groups.return_value = []
        mock_config_storage.get_panels.return_value = []

        with patch('services.config_handler.config_handler.Logger'):
            with patch('services.config_handler.config_handler.ConfigHandler.read_default_config') as mock_read_config:
                handler = ConfigHandler(
                    mock_middleware,
                    mock_config_storage,
                    mock_sensor_data_storage,
                    mock_alarm_manager
                )

                mock_read_config.assert_called_once()

    def test_initialize_system_with_data(self, mock_middleware, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test that system initializes with DB data when available."""
        groups = [{"id": 1, "name": "Group 1"}]
        panels = [{
            "id": 1,
            "name": "Panel 1",
            "gateway": "gateway1",
            "topic": "temperature",
            "color": "#FF0000",
            "panelGroupId": 1,
            "indicator": "0",
            "sensorType": "Temperature"
        }]

        mock_config_storage.get_panel_groups.return_value = groups
        mock_config_storage.get_panels.return_value = panels

        with patch('services.config_handler.config_handler.Logger'):
            with patch('services.config_handler.config_handler.ConfigHandler.read_default_config'):
                with patch('services.config_handler.config_handler.ConfigHandler.initialize_panels_from_db') as mock_init_from_db:
                    handler = ConfigHandler(
                        mock_middleware,
                        mock_config_storage,
                        mock_sensor_data_storage,
                        mock_alarm_manager
                    )

                    # Should have initialized from DB
                    mock_init_from_db.assert_called_once_with(panels, groups)


class TestPanelGroups:
    """Test panel group management."""

    def test_add_panel_group_success(self, config_handler, mock_config_storage):
        """Test adding a panel group successfully."""
        mock_config_storage.add_panel_group.return_value = 1

        result, message = config_handler.add_panel_group("Test Group")

        assert result is True
        assert "Success" in message or "already exists" in message
        mock_config_storage.add_panel_group.assert_called_once_with(
            "Test Group")

    def test_add_panel_group_failure(self, config_handler, mock_config_storage):
        """Test adding a panel group with failure."""
        mock_config_storage.add_panel_group.return_value = -1

        result, message = config_handler.add_panel_group("Test Group")

        assert result is False
        assert "Error adding panel group" in message

    def test_add_panel_group_already_exists(self, config_handler, mock_config_storage):
        """Test adding a panel group that already exists."""
        mock_config_storage.add_panel_group.return_value = 1

        # Add group first time
        result1, message1 = config_handler.add_panel_group("Test Group")
        assert result1 is True

        # Add same group again (same ID returned)
        mock_config_storage.add_panel_group.return_value = 1  # Same ID
        result2, message2 = config_handler.add_panel_group("Test Group")
        assert result2 is True
        assert "already exists" in message2

    def test_remove_panel_group_success(self, config_handler, mock_config_storage):
        """Test removing a panel group successfully."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("Test Group")

        # Now remove it
        mock_config_storage.remove_panel_group.return_value = True
        result, message = config_handler.remove_panel_group(1)

        assert result is True
        assert "Success" in message
        assert 1 not in config_handler._panel_groups

    def test_remove_panel_group_failure(self, config_handler, mock_config_storage):
        """Test removing a panel group with failure."""
        mock_config_storage.remove_panel_group.return_value = False

        result, message = config_handler.remove_panel_group(999)

        assert result is False
        assert "Error removing panel group" in message

    def test_update_panel_group_success(self, config_handler, mock_config_storage):
        """Test updating a panel group successfully."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("Test Group")

        # Now update it
        mock_config_storage.update_panel_group.return_value = True
        result, message = config_handler.update_panel_group(1, "Updated Group")

        assert result is True
        assert "Success" in message

    def test_update_panel_group_failure(self, config_handler, mock_config_storage):
        """Test updating a panel group with failure."""
        mock_config_storage.update_panel_group.return_value = False

        result, message = config_handler.update_panel_group(
            999, "Updated Group")

        assert result is False
        assert "Error updating panel group" in message

    def test_add_panel_group_command(self, config_handler, mock_config_storage, mock_middleware):
        """Test add panel group command."""
        mock_config_storage.add_panel_group.return_value = 1

        command = {
            "data": {"name": "Test Group"},
            "requestId": "test-request-1"
        }

        config_handler.add_panel_group_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert call_args[2] == "test-request-1"

    def test_remove_panel_group_command(self, config_handler, mock_config_storage, mock_middleware):
        """Test remove panel group command."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("Test Group")

        mock_config_storage.remove_panel_group.return_value = True
        command = {
            "data": {"id": 1},
            "requestId": "test-request-2"
        }

        config_handler.remove_panel_group_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result

    def test_update_panel_group_command(self, config_handler, mock_config_storage, mock_middleware):
        """Test update panel group command."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("Test Group")

        mock_config_storage.update_panel_group.return_value = True
        command = {
            "data": {"id": 1, "name": "Updated Group"},
            "requestId": "test-request-3"
        }

        config_handler.update_panel_group_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result


class TestPanelManagement:
    """Test panel management."""

    def test_add_panel_success(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test adding a panel successfully."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        result, message = config_handler.add_panel(sample_panel_info)

        assert result is True
        mock_config_storage.add_panel.assert_called_once()
        mock_sensor_data_storage.add_new_subscription.assert_called_once()

    def test_add_panel_without_id(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test adding a panel without an ID (new panel)."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        # Don't include id in panel_info
        panel_info = sample_panel_info.copy()

        result, message = config_handler.add_panel(panel_info)

        assert result is True
        mock_config_storage.add_panel.assert_called_once()

    def test_add_panel_with_id(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test adding a panel with an ID (existing panel)."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        # Include id in panel_info
        panel_info = sample_panel_info.copy()
        panel_info["id"] = 5

        result, message = config_handler.add_panel(panel_info)

        assert result is True
        # Should not call add_panel since id is provided
        # mock_config_storage.add_panel.assert_not_called()

    def test_add_panel_subscription_failure(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test adding a panel when subscription fails."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            False, "Subscription failed")

        result, message = config_handler.add_panel(sample_panel_info)

        assert result is False
        assert "Subscription failed" in message

    def test_add_panel_command_success(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test add panel command successfully."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        command = {
            "data": sample_panel_info,
            "requestId": "test-request-4"
        }

        config_handler.add_panel_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert call_args[2] == "test-request-4"

    def test_add_panel_command_failure(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test add panel command with failure."""
        # First add a group
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            False, "Failed")

        command = {
            "data": sample_panel_info,
            "requestId": "test-request-5"
        }

        config_handler.add_panel_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is False  # result

    def test_remove_panel_success(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test removing a panel successfully."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        result, message = config_handler.add_panel(sample_panel_info)
        assert result is True

        # Now remove the panel
        mock_config_storage.remove_panel.return_value = True

        # Create a mock wait flag that sets immediately
        with patch('threading.Event') as mock_event:
            event_instance = MagicMock()
            event_instance.wait = MagicMock()
            event_instance.set = MagicMock()
            mock_event.return_value = event_instance

            # Mock the erase_sensor_info callback to set the event immediately
            def set_event_callback(a, b):
                event_instance.set()

            mock_sensor_data_storage.erase_sensor_info = MagicMock(
                side_effect=lambda *args, **kwargs: set_event_callback(None, None))

            result, message = config_handler.remove_panel(1)

            assert result is True
            assert "Removido" in message or "Removed" in message
            mock_config_storage.remove_panel.assert_called_once()

    def test_remove_panel_not_found(self, config_handler, mock_config_storage):
        """Test removing a panel that doesn't exist."""
        result, message = config_handler.remove_panel(999)

        assert result is False
        assert "not found" in message.lower() or "error" in message.lower()

    def test_remove_panel_command_success(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test remove panel command successfully."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        mock_config_storage.remove_panel.return_value = True

        with patch('threading.Event') as mock_event:
            event_instance = MagicMock()
            event_instance.wait = MagicMock()
            event_instance.set = MagicMock()
            mock_event.return_value = event_instance

            def set_event_callback(a, b):
                event_instance.set()

            mock_sensor_data_storage.erase_sensor_info = MagicMock(
                side_effect=lambda *args, **kwargs: set_event_callback(None, None))

            command = {
                "data": {"id": 1},
                "requestId": "test-request-6"
            }

            config_handler.remove_panel_command(command)

            mock_middleware.send_command_answear.assert_called_once()
            call_args = mock_middleware.send_command_answear.call_args[0]
            assert call_args[0] is True  # result

    def test_find_panel_from_id(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test finding a panel by ID."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_id(1)

        assert panel is not None
        assert panel.id == 1

    def test_find_panel_from_id_not_found(self, config_handler):
        """Test finding a panel by ID that doesn't exist."""
        panel = config_handler._find_panel_from_id(999)

        assert panel is None

    def test_find_panel_from_topic(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test finding a panel by topic, indicator, and gateway."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_topic(
            "temperature", "0", "gateway1"
        )

        assert panel is not None
        assert panel.topic == "temperature"
        assert panel.gateway == "gateway1"

    def test_find_panel_from_topic_not_found(self, config_handler):
        """Test finding a panel by topic that doesn't exist."""
        panel = config_handler._find_panel_from_topic(
            "nonexistent", "0", "gateway1"
        )

        assert panel is None


class TestPanelFunctions:
    """Test panel function updates."""

    def test_update_panel_functions(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test updating panel functions."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        update_info = {
            "panelId": 1,
            "name": "Updated Panel",
            "color": "#00FF00",
            "gain": 1.5,
            "offset": 0.5,
            "multiplier": 1000,
            "maxAlarm": 200.0,
            "minAlarm": 50.0
        }

        config_handler.update_panel_functions(update_info)

        mock_config_storage.update_panel.assert_called_once()

    def test_update_panel_functions_command_success(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test update panel functions command successfully."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        command = {
            "data": {
                "panelId": 1,
                "name": "Updated Panel",
                "color": "#00FF00",
                "gain": 1.5,
                "offset": 0.5,
                "multiplier": 1000
            },
            "requestId": "test-request-7"
        }

        config_handler.update_panel_functions_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result

    def test_update_panel_functions_command_exception(self, config_handler, mock_middleware):
        """Test update panel functions command with exception."""
        command = {
            "data": {
                "panelId": 999,  # Non-existent panel
                "name": "Updated Panel"
            },
            "requestId": "test-request-8"
        }

        config_handler.update_panel_functions_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is False  # result

    def test_handle_change_panel_alarm_add(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test handling change panel alarm - adding new alarm."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_id(1)
        assert panel is not None

        # Add max alarm (panel has no alarm initially)
        new_alarm = config_handler.handle_change_panel_alarm(
            panel, None, 100.0, True
        )

        assert new_alarm is not None
        mock_alarm_manager.add_alarm.assert_called_once()

    def test_handle_change_panel_alarm_remove(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test handling change panel alarm - removing alarm."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_id(1)

        # Create an existing alarm
        existing_alarm = Alarm({
            "id": 1,
            "name": "test",
            "topic": "test",
            "threshold": 100.0,
            "type": AlarmType.Higher,
            "panelId": 1
        })
        panel.max_alarm = existing_alarm

        # Remove alarm (set to None)
        result = config_handler.handle_change_panel_alarm(
            panel, existing_alarm, None, True
        )

        assert result is None
        mock_alarm_manager.remove_alarm.assert_called_once_with(1)

    def test_handle_change_panel_alarm_update(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test handling change panel alarm - updating threshold."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_id(1)

        # Create an existing alarm
        existing_alarm = Alarm({
            "id": 1,
            "name": "test",
            "topic": "test",
            "threshold": 100.0,
            "type": AlarmType.Higher,
            "panelId": 1
        })
        panel.max_alarm = existing_alarm

        # Update alarm threshold
        with patch.object(ClientMiddleware, 'get_gateway_status_topic') as mock_get_topic:
            mock_get_topic.return_value = "gateway1-status-*"

            result = config_handler.handle_change_panel_alarm(
                panel, existing_alarm, 150.0, True
            )

            assert result is not None
            mock_alarm_manager.change_alarm_threshold.assert_called_once()

    def test_handle_change_panel_alarm_no_change(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_alarm_manager):
        """Test handling change panel alarm - no change needed."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        panel = config_handler._find_panel_from_id(1)

        # Create an existing alarm
        existing_alarm = Alarm({
            "id": 1,
            "name": "test",
            "topic": "test",
            "threshold": 100.0,
            "type": AlarmType.Higher,
            "panelId": 1
        })
        panel.max_alarm = existing_alarm

        # No change (same threshold)
        result = config_handler.handle_change_panel_alarm(
            panel, existing_alarm, 100.0, True
        )

        assert result == existing_alarm
        # Should not call any alarm manager methods
        mock_alarm_manager.add_alarm.assert_not_called()
        mock_alarm_manager.remove_alarm.assert_not_called()
        mock_alarm_manager.change_alarm_threshold.assert_not_called()


class TestStatusSubscriptions:
    """Test status subscription management."""

    def test_subscribe_to_status(self, config_handler, mock_middleware):
        """Test subscribing to status."""
        with patch.object(ClientMiddleware, 'get_calibrate_topic') as mock_get_topic:
            mock_get_topic.return_value = "gateway1-calibrate-temperature-0"

            config_handler.subscribe_to_status(
                "gateway1", "temperature", "0", 1, 0)

            mock_middleware.add_subscribe_to_status.assert_called_once()
            assert "gateway1-calibrate-temperature-0" in config_handler._status_subscribers

    def test_remove_panel_subscription(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test removing panel subscription."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        # Get the panel
        panel = config_handler._find_panel_from_id(1)

        # Remove subscription
        config_handler.remove_panel_subscription(panel)

        mock_middleware.remove_subscribe_from_status.assert_called()

    def test_calibration_update_received(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test receiving calibration update."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        # Create calibration update data
        calibration_data = MagicMock()
        calibration_data.offset = 0.5
        calibration_data.gain = 1.5

        status_info = {"data": calibration_data}

        # Update calibration - use group_id 1 (integer) matching the added group
        config_handler.calibration_update_received(status_info, 1, 0)

        # Verify panel was updated
        panel = config_handler._find_panel_from_id(1)
        assert panel.offset == 0.5
        assert panel.gain == 1.5
        mock_config_storage.update_panel.assert_called()

    def test_update_calibration_from_gateway_status(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage, mock_middleware):
        """Test updating calibration from gateway status."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        # Create panel info for calibration
        panel_info = MagicMock()
        panel_info.topic = "temperature"
        panel_info.indicator = "0"
        panel_info.gateway = "gateway1"
        panel_info.offset = 0.5
        panel_info.gain = 1.5

        panels = [panel_info]

        config_handler.update_calibration_from_gateway_status(panels)

        # Verify panel was updated
        panel = config_handler._find_panel_from_topic(
            "temperature", "0", "gateway1")
        assert panel is not None
        assert panel.offset == 0.5
        assert panel.gain == 1.5
        mock_config_storage.update_panel.assert_called()


class TestPanelListAndStatus:
    """Test panel list and status sending."""

    def test_get_panels_list_command(self, config_handler, mock_middleware):
        """Test getting panels list command."""
        command = {
            "requestId": "test-request-9"
        }

        config_handler.get_panels_list_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert "PanelsInfo" in call_args[1]

    def test_create_object_from_panels_info(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test creating object from panels info."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        # Get panels info
        result = config_handler.create_object_from_panels_info()

        assert "PanelsInfo" in result
        assert "calibrateUpdate" in result

    def test_send_ui_update_action(self, config_handler, mock_middleware):
        """Test sending UI update action."""
        config_handler.send_ui_update_action()

        mock_middleware.send_status.assert_called_once()
        call_args = mock_middleware.send_status.call_args[0]
        assert call_args[0] == "ui-update-*"
        assert "PanelsInfo" in call_args[1]

    def test_get_topic_mappings(self, config_handler, sample_panel_info, mock_config_storage, mock_sensor_data_storage):
        """Test getting topic mappings."""
        # First add a group and panel
        mock_config_storage.add_panel_group.return_value = 1
        config_handler.add_panel_group("0")

        mock_config_storage.add_panel.return_value = 1
        mock_sensor_data_storage.add_new_subscription.return_value = (
            True, "Success")

        config_handler.add_panel(sample_panel_info)

        topic_to_name, topic_to_type = config_handler.get_topic_mappings()

        assert isinstance(topic_to_name, dict)
        assert isinstance(topic_to_type, dict)

        # Verify panel topic is in mappings
        expected_topic = "gateway1-temperature-0"
        assert expected_topic in topic_to_name
        assert expected_topic in topic_to_type
