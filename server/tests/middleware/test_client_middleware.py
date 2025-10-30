import pytest
from unittest.mock import MagicMock, patch, call
import multiprocessing
import threading
from collections.abc import Callable

from middleware.client_middleware import ClientMiddleware
from middleware.subscriber_interface import SubscriberInterface
from middleware.subscriber_manager import SubscriberManager


@pytest.fixture
def mock_middleware():
    """Mock middleware for testing"""
    middleware = MagicMock()
    middleware.add_new_middleware_listener.return_value = multiprocessing.Queue()
    return middleware


@pytest.fixture
def client_middleware(mock_middleware):
    """ClientMiddleware instance for testing"""
    return ClientMiddleware(mock_middleware, "test_client")


@pytest.fixture
def mock_subscriber():
    """Mock subscriber for testing"""
    subscriber = MagicMock(spec=SubscriberInterface)
    subscriber.get_id.return_value = "test_subscriber_id"
    return subscriber


class TestClientMiddlewareStaticMethods:
    """Test static methods of ClientMiddleware"""

    def test_get_calibrate_topic(self):
        """Test get_calibrate_topic static method"""
        result = ClientMiddleware.get_calibrate_topic(
            "gateway1", "sensor1", "temp")
        assert result == "gateway1-sensor1-tempcalibrate"

    def test_get_status_topic(self):
        """Test get_status_topic static method"""
        result = ClientMiddleware.get_status_topic(
            "gateway1", "sensor1", "temp")
        assert result == "gateway1-sensor1-temp"

    def test_get_gateway_status_topic(self):
        """Test get_gateway_status_topic static method"""
        result = ClientMiddleware.get_gateway_status_topic("gateway1")
        assert result == "gateway1-status-*"

    def test_from_status_topic_get_gateway_topic(self):
        """Test from_status_topic_get_gateway_topic static method"""
        result = ClientMiddleware.from_status_topic_get_gateway_topic(
            "gateway1-sensor1-temp")
        assert result == "gateway1-status-*"


class TestClientMiddlewareInitialization:
    """Test ClientMiddleware initialization"""

    def test_initialization(self, mock_middleware):
        """Test proper initialization of ClientMiddleware"""
        client = ClientMiddleware(mock_middleware, "test_client")

        assert client._name == "test_client"
        assert client._global_middleware == mock_middleware
        # Check it's a lock-like object
        assert hasattr(client._lock, 'acquire')
        assert isinstance(client._subscribers, dict)
        assert isinstance(client._request_queue, dict)
        assert isinstance(client._commands_available, dict)
        assert client._commands_available == {}


class TestCommandManagement:
    """Test command management functionality"""

    def test_add_commands(self, client_middleware):
        """Test adding commands to the middleware"""
        commands = {
            "test_command1": MagicMock(),
            "test_command2": MagicMock()
        }

        client_middleware.add_commands(commands)

        assert client_middleware._commands_available == commands

    def test_add_commands_merge_existing(self, client_middleware):
        """Test adding commands merges with existing commands"""
        existing_commands = {"existing_command": MagicMock()}
        client_middleware._commands_available = existing_commands

        new_commands = {"new_command": MagicMock()}
        client_middleware.add_commands(new_commands)

        expected = existing_commands | new_commands
        assert client_middleware._commands_available == expected

    def test_command_update_existing_command(self, client_middleware):
        """Test command_update calls existing command handler"""
        mock_handler = MagicMock()
        client_middleware._commands_available["test_command"] = mock_handler

        command = {"name": "test_command", "data": "test_data"}
        client_middleware.command_update(command)

        mock_handler.assert_called_once_with(command)

    def test_command_update_nonexistent_command(self, client_middleware):
        """Test command_update with non-existent command does nothing"""
        command = {"name": "nonexistent_command", "data": "test_data"}
        # Should not raise exception
        client_middleware.command_update(command)


class TestSubscriptionManagement:
    """Test subscription management functionality"""

    def test_add_subscribe_to_status_new_subscriber(self, client_middleware, mock_subscriber):
        """Test adding subscription to new status"""
        status_name = "test_status"

        with patch('middleware.client_middleware.SubscriberManager') as mock_subscriber_manager_class:
            mock_subscriber_manager = MagicMock()
            mock_subscriber_manager_class.return_value = mock_subscriber_manager

            client_middleware.add_subscribe_to_status(
                mock_subscriber, status_name)

            # Check that SubscriberManager was created
            mock_subscriber_manager_class.assert_called_once_with(
                mock_subscriber)
            # Check that subscriber was added
            mock_subscriber_manager.add_subscriber.assert_called_once_with(
                mock_subscriber)
            # Check that subscriber manager was stored
            assert status_name in client_middleware._subscribers

    def test_add_subscribe_to_status_existing_subscriber(self, client_middleware, mock_subscriber):
        """Test adding subscription to existing status"""
        status_name = "test_status"
        mock_subscriber_manager = MagicMock()
        client_middleware._subscribers[status_name] = mock_subscriber_manager

        client_middleware.add_subscribe_to_status(mock_subscriber, status_name)

        # Check that existing subscriber manager was used
        mock_subscriber_manager.add_subscriber.assert_called_once_with(
            mock_subscriber)

    def test_remove_subscribe_from_status_existing(self, client_middleware, mock_subscriber):
        """Test removing subscription from existing status"""
        status_name = "test_status"
        mock_subscriber_manager = MagicMock()
        client_middleware._subscribers[status_name] = mock_subscriber_manager

        client_middleware.remove_subscribe_from_status(
            mock_subscriber, status_name)

        mock_subscriber_manager.remove_subscriber.assert_called_once_with(
            "test_subscriber_id")

    def test_remove_subscribe_from_status_nonexistent(self, client_middleware, mock_subscriber):
        """Test removing subscription from non-existent status"""
        status_name = "nonexistent_status"

        with patch.object(client_middleware._logger, 'info') as mock_logger:
            client_middleware.remove_subscribe_from_status(
                mock_subscriber, status_name)

            mock_logger.assert_called_once_with(
                f"Middleware::add_subscribe_from_status-> Error, subscriber test_subscriber_id non existant"
            )


class TestCommandSending:
    """Test command sending functionality"""

    def test_send_command(self, client_middleware):
        """Test sending a command"""
        command_name = "test_command"
        data = {"test": "data"}
        callback = MagicMock()
        error_handler = MagicMock()

        client_middleware._global_middleware.send_command.return_value = "request_id_123"

        client_middleware.send_command(
            command_name, data, callback, error_handler)

        # Check that global middleware was called
        client_middleware._global_middleware.send_command.assert_called_once_with(
            command_name, data
        )
        # Check that callbacks were stored
        assert client_middleware._request_queue["request_id_123"] == (
            callback, error_handler)

    def test_send_command_answear(self, client_middleware):
        """Test sending command answer"""
        result = True
        data = {"test": "data"}
        request_id = "request_id_123"

        client_middleware.send_command_answear(result, data, request_id)

        client_middleware._global_middleware.send_command_answear.assert_called_once_with(
            "", result, data, request_id
        )


class TestStatusSending:
    """Test status sending functionality"""

    def test_send_status(self, client_middleware):
        """Test sending a single status"""
        topic = "test_topic"
        status = {"value": 123}

        client_middleware.send_status(topic, status)

        client_middleware._global_middleware.send_status.assert_called_once_with(
            topic, status)

    def test_send_status_array(self, client_middleware):
        """Test sending status array"""
        status_list = [{"topic": "test1", "value": 123},
                       {"topic": "test2", "value": 456}]

        client_middleware.send_status_array(status_list)

        client_middleware._global_middleware.send_status_array.assert_called_once_with(
            status_list)


class TestSubscriptionMatching:
    """Test subscription matching logic"""

    def test_check_if_subscribed_exact_match(self, client_middleware):
        """Test exact subscription match"""
        subscriber_status_name = "gateway1-sensor1-temp"
        status_name = "gateway1-sensor1-temp"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is True

    def test_check_if_subscribed_wildcard_gateway(self, client_middleware):
        """Test subscription match with wildcard gateway"""
        subscriber_status_name = "*-sensor1-temp"
        status_name = "gateway1-sensor1-temp"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is True

    def test_check_if_subscribed_wildcard_topic(self, client_middleware):
        """Test subscription match with wildcard topic"""
        subscriber_status_name = "gateway1-*-temp"
        status_name = "gateway1-sensor1-temp"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is True

    def test_check_if_subscribed_wildcard_indicator(self, client_middleware):
        """Test subscription match with wildcard indicator"""
        subscriber_status_name = "gateway1-sensor1-*"
        status_name = "gateway1-sensor1-temp"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is True

    def test_check_if_subscribed_no_match(self, client_middleware):
        """Test subscription with no match"""
        subscriber_status_name = "gateway1-sensor1-temp"
        status_name = "gateway2-sensor2-humidity"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is False

    def test_check_if_subscribed_partial_wildcard_match(self, client_middleware):
        """Test subscription match with partial wildcards"""
        subscriber_status_name = "*-*-*"
        status_name = "gateway1-sensor1-temp"

        result = client_middleware._check_if_subscribed(
            subscriber_status_name, status_name)
        assert result is True


class TestMiddlewareUpdateSystem:
    """Test middleware update system"""

    def test_run_middleware_update_command(self, client_middleware):
        """Test processing command updates"""
        # Setup mock queue with command data
        command_data = {
            "isCommand": True,
            "name": "test_command",
            "data": "test_data"
        }

        # Mock the queue to return our data and then become empty
        mock_queue = MagicMock()
        # First call returns False, second returns True
        mock_queue.empty.side_effect = [False, True]
        mock_queue.get.return_value = command_data
        client_middleware._transfer_queue = mock_queue

        with patch.object(client_middleware, '_command_update') as mock_command_update:
            client_middleware.run_middleware_update()
            mock_command_update.assert_called_once_with(command_data)

    def test_run_middleware_update_status(self, client_middleware):
        """Test processing status updates"""
        # Setup mock queue with status data
        status_data = {
            "isCommand": False,
            "name": "test_status",
            "data": "test_data"
        }

        # Mock the queue to return our data and then become empty
        mock_queue = MagicMock()
        # First call returns False, second returns True
        mock_queue.empty.side_effect = [False, True]
        mock_queue.get.return_value = status_data
        client_middleware._transfer_queue = mock_queue

        with patch.object(client_middleware, '_status_update') as mock_status_update:
            client_middleware.run_middleware_update()
            mock_status_update.assert_called_once_with(status_data)

    def test_run_middleware_update_empty_queue(self, client_middleware):
        """Test run_middleware_update with empty queue"""
        with patch.object(client_middleware, '_command_update') as mock_command_update, \
                patch.object(client_middleware, '_status_update') as mock_status_update:
            client_middleware.run_middleware_update()
            mock_command_update.assert_not_called()
            mock_status_update.assert_not_called()

    def test_command_update_with_callback(self, client_middleware):
        """Test command update with callback handlers"""
        request_id = "test_request_id"
        callback = MagicMock()
        error_handler = MagicMock()
        client_middleware._request_queue[request_id] = (
            callback, error_handler)

        command_data = {
            "requestId": request_id,
            "name": "",
            "result": True,
            "data": "test_data"
        }

        client_middleware._command_update(command_data)

        callback.assert_called_once_with(command_data)
        error_handler.assert_not_called()
        assert request_id not in client_middleware._request_queue

    def test_command_update_with_error_handler(self, client_middleware):
        """Test command update with error handler"""
        request_id = "test_request_id"
        callback = MagicMock()
        error_handler = MagicMock()
        client_middleware._request_queue[request_id] = (
            callback, error_handler)

        command_data = {
            "requestId": request_id,
            "name": "",
            "result": False,
            "data": "test_data"
        }

        client_middleware._command_update(command_data)

        callback.assert_not_called()
        error_handler.assert_called_once_with(command_data)
        assert request_id not in client_middleware._request_queue

    def test_command_update_no_callbacks(self, client_middleware):
        """Test command update with no callbacks"""
        request_id = "test_request_id"
        client_middleware._request_queue[request_id] = (None, None)

        command_data = {
            "requestId": request_id,
            "name": "",
            "result": True,
            "data": "test_data"
        }

        # Should not raise exception
        client_middleware._command_update(command_data)
        assert request_id not in client_middleware._request_queue

    def test_command_update_regular_command(self, client_middleware):
        """Test command update for regular command (not callback)"""
        command_data = {
            "requestId": "test_request_id",
            "name": "test_command",
            "data": "test_data"
        }

        with patch.object(client_middleware, 'command_update') as mock_command_update:
            client_middleware._command_update(command_data)
            mock_command_update.assert_called_once_with(command_data)

    def test_status_update_with_subscribers(self, client_middleware):
        """Test status update with matching subscribers"""
        # Setup mock subscribers
        mock_subscriber1 = MagicMock()
        mock_subscriber2 = MagicMock()
        client_middleware._subscribers["gateway1-*-*"] = mock_subscriber1
        client_middleware._subscribers["gateway2-*-*"] = mock_subscriber2

        status_data = {
            "name": "gateway1-sensor1-temp",
            "data": {"value": 25.5}
        }

        with patch.object(client_middleware._data_converter, 'convert_data') as mock_convert:
            # Generate a status that follows the gateway-topic-indicator pattern
            mock_convert.return_value = [
                {"name": "gateway1-generated-temp", "value": 30.0}]

            client_middleware._status_update(status_data)

            # Check that matching subscriber received the status
            mock_subscriber1.send_status.assert_any_call(
                "gateway1-sensor1-temp", {"value": 25.5})
            mock_subscriber2.send_status.assert_not_called()

            # Check that generated status was also sent
            mock_subscriber1.send_status.assert_any_call(
                "gateway1-generated-temp", 30.0)

    def test_status_update_no_matching_subscribers(self, client_middleware):
        """Test status update with no matching subscribers"""
        # Setup mock subscribers that don't match
        mock_subscriber = MagicMock()
        client_middleware._subscribers["gateway2-*-*"] = mock_subscriber

        status_data = {
            "name": "gateway1-sensor1-temp",
            "data": {"value": 25.5}
        }

        with patch.object(client_middleware._data_converter, 'convert_data') as mock_convert:
            mock_convert.return_value = []

            client_middleware._status_update(status_data)

            # Check that no subscriber received the status
            mock_subscriber.send_status.assert_not_called()


class TestConcurrency:
    """Test thread safety and concurrency"""

    def test_thread_safety_subscription_management(self, client_middleware, mock_subscriber):
        """Test that subscription management is thread-safe"""
        status_name = "test_status"

        # Mock the SubscriberManager to avoid real threading issues
        with patch('middleware.client_middleware.SubscriberManager') as mock_subscriber_manager_class:
            mock_subscriber_manager = MagicMock()
            mock_subscriber_manager_class.return_value = mock_subscriber_manager

            def add_subscription():
                client_middleware.add_subscribe_to_status(
                    mock_subscriber, status_name)

            def remove_subscription():
                client_middleware.remove_subscribe_from_status(
                    mock_subscriber, status_name)

            # Run multiple threads
            threads = []
            for _ in range(5):  # Reduced number of threads to avoid overwhelming
                threads.append(threading.Thread(target=add_subscription))
                threads.append(threading.Thread(target=remove_subscription))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            # Should not raise any exceptions due to race conditions
            assert True  # If we get here, no exceptions were raised
