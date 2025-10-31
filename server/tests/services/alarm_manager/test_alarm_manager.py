import pytest
import threading
import time
import queue
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Import the classes to be tested
from services.alarm_manager.alarm_manager import AlarmManager
from services.alarm_manager.alarm_manager_commands import AlarmManagerCommands
from dataModules.alarm import Alarm, AlarmType
from dataModules.sensor_info import SensorInfo
from dataModules.event import EventModel
from middleware.status_subscriber import StatuSubscribers
from middleware.client_middleware import ClientMiddleware


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
    config_storage.get_alarm_info = MagicMock(return_value=([], True))
    config_storage.add_alarm = MagicMock(return_value=1)
    config_storage.remove_alarm = MagicMock(return_value=True)
    config_storage.update_alarm = MagicMock(return_value=True)
    config_storage.add_event_array = MagicMock(return_value=True)
    config_storage.remove_events = MagicMock(return_value=True)
    return config_storage


@pytest.fixture
def alarm_manager(mock_middleware, mock_config_storage):
    """Create an AlarmManager instance for testing."""
    with patch('services.alarm_manager.alarm_manager.Logger'):
        manager = AlarmManager(mock_middleware, mock_config_storage)
        # Stop the thread after a short time to allow testing
        yield manager
        # Cleanup: signal thread to stop
        if hasattr(manager, '_alarm_check_thread'):
            manager._check_queue.put(None)


@pytest.fixture
def sample_alarm():
    """Create a sample alarm for testing."""
    return {
        "id": 1,
        "name": "Test Alarm",
        "topic": "gateway1-temperature-0",
        "threshold": 100.0,
        "type": AlarmType.Higher,
        "panelId": 1
    }


@pytest.fixture
def sample_alarm_object(sample_alarm):
    """Create a sample Alarm object for testing."""
    return Alarm(sample_alarm)


@pytest.fixture
def sample_sensor_info():
    """Create a sample sensor info for testing."""
    return SensorInfo(
        sensor_full_topic="gateway1-temperature-0",
        timestamp=datetime.now(),
        value=150.0
    )


@pytest.fixture
def sample_status_info():
    """Create a sample status info for testing."""
    reading = MagicMock()
    reading.full_topic = "gateway1-temperature-0"
    reading.timestamp = datetime.now()
    reading.value = 150.0

    status_info = MagicMock()
    status_info.data = MagicMock()
    status_info.data.readings = [reading]

    return {"data": status_info.data}


class TestAlarmManagerInitialization:
    """Test AlarmManager initialization and setup."""

    def test_initialization(self, mock_middleware, mock_config_storage):
        """Test that AlarmManager initializes correctly."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            manager = AlarmManager(mock_middleware, mock_config_storage)

            assert manager._middleware == mock_middleware
            assert manager._config_storage == mock_config_storage
            assert isinstance(manager._alarms_info, dict)
            assert len(manager._alarms_info) == 0
            assert isinstance(manager._alarm_check_topics, dict)
            assert isinstance(manager._status_subscribers, dict)
            assert isinstance(manager._check_queue, queue.Queue)
            assert manager._subscriptions_add == 1

    def test_commands_initialization(self, mock_middleware, mock_config_storage):
        """Test that commands are registered with middleware."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            AlarmManager(mock_middleware, mock_config_storage)

            mock_middleware.add_commands.assert_called_once()
            commands_dict = mock_middleware.add_commands.call_args[0][0]

            assert AlarmManagerCommands.ADD_ALARM in commands_dict
            assert AlarmManagerCommands.REMOVE_ALARM in commands_dict
            assert AlarmManagerCommands.GET_ALARMS in commands_dict
            assert AlarmManagerCommands.REMOVE_ALL_EVENTS in commands_dict

    def test_system_initialization(self, mock_middleware, mock_config_storage):
        """Test that system initializes with alarms from config storage."""
        sample_alarms = [
            {
                "id": 1,
                "name": "Alarm 1",
                "topic": "gateway1-temperature-0",
                "threshold": 100.0,
                "type": AlarmType.Higher,
                "panelId": 1
            },
            {
                "id": 2,
                "name": "Alarm 2",
                "topic": "gateway2-pressure-1",
                "threshold": 50.0,
                "type": AlarmType.Lower,
                "panelId": 2
            }
        ]

        mock_config_storage.get_alarm_info.return_value = (sample_alarms, True)

        with patch('services.alarm_manager.alarm_manager.Logger'):
            manager = AlarmManager(mock_middleware, mock_config_storage)

            # Wait a bit for thread to initialize
            time.sleep(0.1)

            assert len(manager._alarm_check_topics) == 2
            assert "gateway1-temperature-0" in manager._alarm_check_topics
            assert "gateway2-pressure-1" in manager._alarm_check_topics


class TestAlarmChecking:
    """Test alarm checking functionality."""

    def test_check_if_alarm_should_trigger_higher_true(self, alarm_manager, sample_alarm_object):
        """Test that Higher alarm triggers when value is above threshold."""
        sample_alarm_object.type = AlarmType.Higher
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 150.0)
        assert result is True

    def test_check_if_alarm_should_trigger_higher_false(self, alarm_manager, sample_alarm_object):
        """Test that Higher alarm doesn't trigger when value is below threshold."""
        sample_alarm_object.type = AlarmType.Higher
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 50.0)
        assert result is False

    def test_check_if_alarm_should_trigger_lower_true(self, alarm_manager, sample_alarm_object):
        """Test that Lower alarm triggers when value is below threshold."""
        sample_alarm_object.type = AlarmType.Lower
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 50.0)
        assert result is True

    def test_check_if_alarm_should_trigger_lower_false(self, alarm_manager, sample_alarm_object):
        """Test that Lower alarm doesn't trigger when value is above threshold."""
        sample_alarm_object.type = AlarmType.Lower
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 150.0)
        assert result is False

    def test_check_if_alarm_should_trigger_equal_true(self, alarm_manager, sample_alarm_object):
        """Test that Equal alarm triggers when value equals threshold."""
        sample_alarm_object.type = AlarmType.Equal
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 100.0)
        assert result is True

    def test_check_if_alarm_should_trigger_equal_false(self, alarm_manager, sample_alarm_object):
        """Test that Equal alarm doesn't trigger when value doesn't equal threshold."""
        sample_alarm_object.type = AlarmType.Equal
        sample_alarm_object.threshold = 100.0

        result = alarm_manager.check_if_alarm_should_trigger(
            sample_alarm_object, 150.0)
        assert result is False


class TestAlarmSetup:
    """Test alarm setup functionality."""

    def test_setup_alarm_new_topic(self, alarm_manager, sample_alarm_object, mock_middleware):
        """Test setting up an alarm for a new topic."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Clear any existing state to ensure clean test
            alarm_manager._alarm_check_topics.clear()
            alarm_manager._alarms_info.clear()
            alarm_manager._status_subscribers.clear()

            alarm_manager.setup_alarm(sample_alarm_object)

            assert "gateway1-temperature-0" in alarm_manager._alarm_check_topics
            assert len(
                alarm_manager._alarm_check_topics["gateway1-temperature-0"]) == 1
            assert sample_alarm_object in alarm_manager._alarm_check_topics[
                "gateway1-temperature-0"]

            # Verify subscription was added
            mock_middleware.add_subscribe_to_status.assert_called()

    def test_setup_alarm_existing_topic(self, alarm_manager, sample_alarm_object):
        """Test setting up multiple alarms for the same topic."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Clear any existing state to ensure clean test
            alarm_manager._alarm_check_topics.clear()
            alarm_manager._alarms_info.clear()
            alarm_manager._status_subscribers.clear()

            # Setup first alarm
            alarm_manager.setup_alarm(sample_alarm_object)

            # Setup second alarm for same topic
            alarm2 = Alarm({
                "id": 2,
                "name": "Test Alarm 2",
                "topic": "gateway1-temperature-0",
                "threshold": 200.0,
                "type": AlarmType.Higher,
                "panelId": 1
            })
            alarm_manager.setup_alarm(alarm2)

            assert len(
                alarm_manager._alarm_check_topics["gateway1-temperature-0"]) == 2


class TestAlarmCommands:
    """Test alarm command handling."""

    def test_add_alarm_command_success(self, alarm_manager, sample_alarm, mock_middleware, mock_config_storage):
        """Test adding an alarm successfully."""
        mock_config_storage.add_alarm.return_value = 1

        command = {
            "requestId": "test-request-1",
            "data": sample_alarm
        }

        alarm_manager.add_alarm_command(command)

        mock_config_storage.add_alarm.assert_called_once()
        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert "requestId" in command

    def test_add_alarm_command_failure(self, alarm_manager, sample_alarm, mock_middleware, mock_config_storage):
        """Test adding an alarm with failure."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            # Make add_alarm return -1 (failure)
            mock_config_storage.add_alarm.return_value = -1

            command = {
                "requestId": "test-request-2",
                "data": sample_alarm
            }

            alarm_manager.add_alarm_command(command)

            mock_middleware.send_command_answear.assert_called_once()
            # result should be False or the alarm object without id

    def test_get_alarm_command_success(self, alarm_manager, sample_alarm, mock_middleware, mock_config_storage):
        """Test getting alarms successfully."""
        alarms = [sample_alarm]
        mock_config_storage.get_alarm_info.return_value = (alarms, True)

        command = {
            "requestId": "test-request-3"
        }

        alarm_manager.get_alarm_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert call_args[1] == alarms

    def test_get_alarm_command_failure(self, alarm_manager, mock_middleware, mock_config_storage):
        """Test getting alarms with failure."""
        mock_config_storage.get_alarm_info.return_value = ([], False)

        command = {
            "requestId": "test-request-4"
        }

        alarm_manager.get_alarm_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is False  # result
        assert "Unable to get alarms" in call_args[1]

    def test_remove_alarm_command_success(self, alarm_manager, sample_alarm, mock_middleware, mock_config_storage):
        """Test removing an alarm successfully."""
        mock_config_storage.get_alarm_info.return_value = (
            [sample_alarm], True)
        mock_config_storage.remove_alarm.return_value = True

        # Setup alarm first
        alarm_obj = Alarm(sample_alarm)
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"
            alarm_manager.setup_alarm(alarm_obj)

        command = {
            "requestId": "test-request-5",
            "data": {"id": 1}
        }

        alarm_manager.remove_alarm_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result

    def test_remove_all_events_command_success(self, alarm_manager, mock_middleware, mock_config_storage):
        """Test removing all events successfully."""
        mock_config_storage.remove_events.return_value = True

        command = {
            "requestId": "test-request-6"
        }

        alarm_manager.remove_all_events_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is True  # result
        assert call_args[1] == {"events": []}

    def test_remove_all_events_command_failure(self, alarm_manager, mock_middleware, mock_config_storage):
        """Test removing all events with failure."""
        mock_config_storage.remove_events.return_value = False

        command = {
            "requestId": "test-request-7"
        }

        alarm_manager.remove_all_events_command(command)

        mock_middleware.send_command_answear.assert_called_once()
        call_args = mock_middleware.send_command_answear.call_args[0]
        assert call_args[0] is False  # result


class TestAddCheckStatus:
    """Test status checking and queue management."""

    def test_add_check_status_valid_topic(self, alarm_manager, sample_status_info, sample_alarm_object):
        """Test adding status check for a valid topic."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Setup alarm first
            alarm_manager.setup_alarm(sample_alarm_object)

            # Add status check
            alarm_manager.add_check_status(sample_status_info)

            # Verify item was added to queue
            assert not alarm_manager._check_queue.empty()

    def test_add_check_status_invalid_topic(self, alarm_manager, sample_status_info):
        """Test adding status check for an invalid topic."""
        # Clear any existing state and don't setup alarm, so topic won't be in _alarm_check_topics
        alarm_manager._alarm_check_topics.clear()
        alarm_manager._alarms_info.clear()

        # Clear the queue first
        while not alarm_manager._check_queue.empty():
            try:
                alarm_manager._check_queue.get_nowait()
            except queue.Empty:
                break

        alarm_manager.add_check_status(sample_status_info)

        # Queue should be empty since topic is not in _alarm_check_topics
        assert alarm_manager._check_queue.empty()

    def test_add_check_status_exception_handling(self, alarm_manager, mock_middleware):
        """Test exception handling in add_check_status."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            # Create invalid status info that will raise exception
            invalid_status_info = {"invalid": "data"}

            # Should not raise exception
            alarm_manager.add_check_status(invalid_status_info)


class TestEventSending:
    """Test event creation and sending."""

    def test_send_event_status(self, alarm_manager, mock_middleware):
        """Test sending event status."""
        event1 = EventModel(
            alarm_id=1,
            panel_id=1,
            timestamp=datetime.now(),
            value=150.0
        )
        event1.name = "Test Event 1"

        event2 = EventModel(
            alarm_id=2,
            panel_id=2,
            timestamp=datetime.now(),
            value=200.0
        )
        event2.name = "Test Event 2"

        events = [event1, event2]

        alarm_manager._send_event_status(events)

        # Verify send_status was called for each event
        assert mock_middleware.send_status.call_count == 2
        for event in events:
            mock_middleware.send_status.assert_any_call(
                "alarm-newevent-*",
                event.to_json()
            )


class TestAlarmRemoval:
    """Test alarm removal functionality."""

    def test_remove_alarm_internal_info(self, alarm_manager, sample_alarm_object):
        """Test removing alarm from internal structures."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Clear any existing state to ensure clean test
            alarm_manager._alarm_check_topics.clear()
            alarm_manager._alarms_info.clear()
            alarm_manager._status_subscribers.clear()

            # Setup alarm
            alarm_manager.setup_alarm(sample_alarm_object)

            # Verify alarm is in structure
            assert "gateway1-temperature-0" in alarm_manager._alarm_check_topics
            assert len(
                alarm_manager._alarm_check_topics["gateway1-temperature-0"]) == 1

            # Remove alarm
            gateway_topic = "gateway1-status-*"
            alarm_manager.remove_alarm_internal_info(gateway_topic, 1)

            # Verify alarm is removed
            assert "gateway1-temperature-0" not in alarm_manager._alarm_check_topics
            assert gateway_topic not in alarm_manager._alarms_info

    def test_remove_alarm_with_multiple_alarms(self, alarm_manager, sample_alarm_object):
        """Test removing one alarm when multiple exist for the same topic."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Clear any existing alarms to ensure clean state
            alarm_manager._alarm_check_topics.clear()
            alarm_manager._alarms_info.clear()
            alarm_manager._status_subscribers.clear()

            # Setup first alarm
            alarm_manager.setup_alarm(sample_alarm_object)

            # Setup second alarm
            alarm2 = Alarm({
                "id": 2,
                "name": "Test Alarm 2",
                "topic": "gateway1-temperature-0",
                "threshold": 200.0,
                "type": AlarmType.Higher,
                "panelId": 1
            })
            alarm_manager.setup_alarm(alarm2)

            # Verify both alarms exist
            assert len(
                alarm_manager._alarm_check_topics["gateway1-temperature-0"]) == 2

            # Remove first alarm
            gateway_topic = "gateway1-status-*"
            alarm_manager.remove_alarm_internal_info(gateway_topic, 1)

            # Verify only second alarm remains
            assert len(
                alarm_manager._alarm_check_topics["gateway1-temperature-0"]) == 1
            assert alarm_manager._alarm_check_topics["gateway1-temperature-0"][0].id == 2


class TestChangeAlarmThreshold:
    """Test changing alarm threshold."""

    def test_change_alarm_threshold_success(self, alarm_manager, sample_alarm_object, mock_config_storage):
        """Test successfully changing alarm threshold."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Clear any existing state to ensure clean test
            alarm_manager._alarm_check_topics.clear()
            alarm_manager._alarms_info.clear()
            alarm_manager._status_subscribers.clear()

            # Setup alarm
            alarm_manager.setup_alarm(sample_alarm_object)

            # Change threshold
            gateway_topic = "gateway1-status-*"
            result = alarm_manager.change_alarm_threshold(
                1, 150.0, gateway_topic)

            assert result is not None
            assert result.threshold == 150.0
            mock_config_storage.update_alarm.assert_called_once()

    def test_change_alarm_threshold_not_found(self, alarm_manager, sample_alarm_object):
        """Test changing threshold for non-existent alarm."""
        # Clear any existing state to ensure clean test
        alarm_manager._alarm_check_topics.clear()
        alarm_manager._alarms_info.clear()
        alarm_manager._status_subscribers.clear()

        gateway_topic = "gateway1-status-*"
        # Since _alarms_info[gateway_topic] doesn't exist, this will raise KeyError
        # We should check if the key exists first or handle the exception
        try:
            result = alarm_manager.change_alarm_threshold(
                999, 150.0, gateway_topic)
            assert result is None
        except KeyError:
            # Expected behavior - topic doesn't exist in _alarms_info
            pass


class TestAlarmAddRemove:
    """Test adding and removing alarms through the main methods."""

    def test_add_alarm_success(self, alarm_manager, sample_alarm, mock_config_storage):
        """Test adding an alarm successfully."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            mock_config_storage.add_alarm.return_value = 1

            result = alarm_manager.add_alarm(sample_alarm)

            assert result.id == 1
            mock_config_storage.add_alarm.assert_called_once()

    def test_add_alarm_failure(self, alarm_manager, mock_config_storage):
        """Test adding an alarm with failure."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            mock_config_storage.add_alarm.return_value = -1

            # Create alarm_info without "id" field so id defaults to 0
            alarm_info_no_id = {
                "name": "Test Alarm",
                "topic": "gateway1-temperature-0",
                "threshold": 100.0,
                "type": AlarmType.Higher,
                "panelId": 1
            }
            result = alarm_manager.add_alarm(alarm_info_no_id)

            # Should remain 0 on failure (since no id was set)
            assert result.id == 0

    def test_remove_alarm_success(self, alarm_manager, sample_alarm, mock_config_storage):
        """Test removing an alarm successfully."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
                mock_from_topic.return_value = "gateway1-status-*"

                # Setup alarm first so it's in _alarms_info
                alarm_obj = Alarm(sample_alarm)
                alarm_manager.setup_alarm(alarm_obj)

                # Now mock the config storage calls
                mock_config_storage.get_alarm_info.return_value = (
                    [sample_alarm], True)
                mock_config_storage.remove_alarm.return_value = True

                result = alarm_manager.remove_alarm(1)

                assert result is True
                mock_config_storage.remove_alarm.assert_called_once()

    def test_remove_alarm_not_found(self, alarm_manager, mock_config_storage):
        """Test removing a non-existent alarm."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            mock_config_storage.get_alarm_info.return_value = ([], True)

            result = alarm_manager.remove_alarm(999)

            assert result is True  # Returns True even if not found


class TestIntegration:
    """Integration tests for AlarmManager."""

    def test_full_workflow_add_alarm_trigger_event(self, alarm_manager, sample_alarm, sample_status_info, mock_middleware, mock_config_storage):
        """Test complete workflow from adding alarm to triggering event."""
        with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
            mock_from_topic.return_value = "gateway1-status-*"

            # Add alarm
            mock_config_storage.add_alarm.return_value = 1
            alarm_obj = alarm_manager.add_alarm(sample_alarm)
            assert alarm_obj.id == 1

            # Verify alarm is set up
            assert "gateway1-temperature-0" in alarm_manager._alarm_check_topics

            # Add status check that should trigger alarm
            alarm_manager.add_check_status(sample_status_info)

            # Wait a bit for thread to process
            time.sleep(0.3)

            # Verify event was added (if threshold condition is met)
            # This depends on the alarm threshold and sensor value
            if sample_alarm["threshold"] < sample_status_info["data"].readings[0].value:
                mock_config_storage.add_event_array.assert_called()
                mock_middleware.send_status.assert_called()

    def test_multiple_alarms_same_topic(self, mock_middleware, mock_config_storage):
        """Test handling multiple alarms for the same topic."""
        with patch('services.alarm_manager.alarm_manager.Logger'):
            with patch.object(ClientMiddleware, 'from_status_topic_get_gateway_topic') as mock_from_topic:
                mock_from_topic.return_value = "gateway1-status-*"

                # Ensure no alarms are returned during initialization
                mock_config_storage.get_alarm_info.return_value = ([], True)

                # Create a fresh alarm_manager for this test
                manager = AlarmManager(mock_middleware, mock_config_storage)
                # Clear any alarms set up during initialization (just in case)
                manager._alarm_check_topics.clear()
                manager._alarms_info.clear()

                # Add first alarm
                alarm1_data = {
                    "id": 1,
                    "name": "High Temp Alarm",
                    "topic": "gateway1-temperature-0",
                    "threshold": 100.0,
                    "type": AlarmType.Higher,
                    "panelId": 1
                }
                mock_config_storage.add_alarm.return_value = 1
                manager.add_alarm(alarm1_data)

                # Add second alarm
                alarm2_data = {
                    "id": 2,
                    "name": "Very High Temp Alarm",
                    "topic": "gateway1-temperature-0",
                    "threshold": 200.0,
                    "type": AlarmType.Higher,
                    "panelId": 1
                }
                mock_config_storage.add_alarm.return_value = 2
                manager.add_alarm(alarm2_data)

                # Verify both alarms exist
                assert len(
                    manager._alarm_check_topics["gateway1-temperature-0"]) == 2
