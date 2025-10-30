from middleware.middleware import Middleware
from unittest.mock import patch, MagicMock
import sys
import os

# Add the server directory to the path to import middleware
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestMiddlewareInitialization:
    """Test Middleware class initialization."""

    def test_middleware_init(self):
        """Test that Middleware initializes with correct default values."""
        middleware = Middleware()

        assert middleware._logger is not None
        assert isinstance(middleware._subscriber_queues, list)
        assert isinstance(middleware._request_queues, list)
        assert len(middleware._subscriber_queues) == 0
        assert len(middleware._request_queues) == 0


class TestMiddlewareListenerManagement:
    """Test listener management methods."""

    @patch('multiprocessing.Queue')
    def test_add_new_middleware_listener(self, mock_queue_class):
        """Test adding a new middleware listener."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        initial_count = len(middleware._subscriber_queues)

        queue = middleware.add_new_middleware_listener()

        assert queue == mock_queue
        assert len(middleware._subscriber_queues) == initial_count + 1
        assert mock_queue in middleware._subscriber_queues
        mock_queue_class.assert_called_once()

    @patch('multiprocessing.Queue')
    def test_add_new_request_listener(self, mock_queue_class):
        """Test adding a new request listener."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        initial_count = len(middleware._request_queues)

        queue = middleware.add_new_request_listener()

        assert queue == mock_queue
        assert len(middleware._request_queues) == initial_count + 1
        assert mock_queue in middleware._request_queues
        mock_queue_class.assert_called_once()

    @patch('multiprocessing.Queue')
    def test_multiple_listeners(self, mock_queue_class):
        """Test adding multiple listeners."""
        mock_queues = [MagicMock() for _ in range(5)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple middleware listeners
        queue1 = middleware.add_new_middleware_listener()
        queue2 = middleware.add_new_middleware_listener()
        queue3 = middleware.add_new_middleware_listener()

        # Add multiple request listeners
        req_queue1 = middleware.add_new_request_listener()
        req_queue2 = middleware.add_new_request_listener()

        assert len(middleware._subscriber_queues) == 3
        assert len(middleware._request_queues) == 2
        assert queue1 in middleware._subscriber_queues
        assert queue2 in middleware._subscriber_queues
        assert queue3 in middleware._subscriber_queues
        assert req_queue1 in middleware._request_queues
        assert req_queue2 in middleware._request_queues


class TestMiddlewareStatusSending:
    """Test status sending methods."""

    @patch('multiprocessing.Queue')
    def test_send_status_single_subscriber(self, mock_queue_class):
        """Test sending status to a single subscriber."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        status_name = "test_status"
        data = {"value": 42, "timestamp": 1234567890}

        middleware.send_status(status_name, data)

        # Check that message was put in queue
        expected_message = {
            "name": status_name,
            "data": data,
            "isCommand": False
        }
        mock_queue.put.assert_called_once_with(expected_message)

    @patch('multiprocessing.Queue')
    def test_send_status_multiple_subscribers(self, mock_queue_class):
        """Test sending status to multiple subscribers."""
        mock_queues = [MagicMock() for _ in range(3)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple subscribers
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()

        status_name = "multi_status"
        data = {"sensor": "temperature", "value": 25.5}

        middleware.send_status(status_name, data)

        # Check all queues received the message
        expected_message = {
            "name": status_name,
            "data": data,
            "isCommand": False
        }

        for mock_queue in mock_queues:
            mock_queue.put.assert_called_once_with(expected_message)

    def test_send_status_no_subscribers(self):
        """Test sending status when no subscribers exist."""
        middleware = Middleware()

        # Should not raise any exception
        middleware.send_status("test", {"data": "value"})

        # No queues to check, just ensure no exception was raised
        assert True

    @patch('multiprocessing.Queue')
    def test_send_status_array_single_subscriber(self, mock_queue_class):
        """Test sending status array to a single subscriber."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        status_list = [
            {"statusName": "status1", "data": {"value": 1}},
            {"statusName": "status2", "data": {"value": 2}},
            {"statusName": "status3", "data": {"value": 3}}
        ]

        middleware.send_status_array(status_list)

        # Check that all statuses were sent
        assert mock_queue.put.call_count == 3

        # Check each call individually
        calls = mock_queue.put.call_args_list
        expected_messages = [
            {"name": "status1", "data": {"value": 1}, "isCommand": False},
            {"name": "status2", "data": {"value": 2}, "isCommand": False},
            {"name": "status3", "data": {"value": 3}, "isCommand": False}
        ]

        for expected in expected_messages:
            assert any(
                call[0][0] == expected for call in calls), f"Expected message {expected} not found in calls"

    @patch('multiprocessing.Queue')
    def test_send_status_array_multiple_subscribers(self, mock_queue_class):
        """Test sending status array to multiple subscribers."""
        mock_queues = [MagicMock() for _ in range(2)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple subscribers
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()

        status_list = [
            {"statusName": "batch1", "data": {"id": 1}},
            {"statusName": "batch2", "data": {"id": 2}}
        ]

        middleware.send_status_array(status_list)

        # Check both queues received all messages
        expected_messages = [
            {"name": "batch1", "data": {"id": 1}, "isCommand": False},
            {"name": "batch2", "data": {"id": 2}, "isCommand": False}
        ]

        for mock_queue in mock_queues:
            assert mock_queue.put.call_count == 2
            calls = mock_queue.put.call_args_list
            for expected in expected_messages:
                assert any(
                    call[0][0] == expected for call in calls), f"Expected message {expected} not found in calls"

    @patch('multiprocessing.Queue')
    def test_send_status_array_empty_list(self, mock_queue_class):
        """Test sending empty status array."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        middleware.send_status_array([])

        # Queue should not be called
        mock_queue.put.assert_not_called()

    def test_send_status_array_no_subscribers(self):
        """Test sending status array when no subscribers exist."""
        middleware = Middleware()

        # Should not raise any exception
        middleware.send_status_array([{"statusName": "test", "data": {}}])

        # No queues to check, just ensure no exception was raised
        assert True


class TestMiddlewareCommandSending:
    """Test command sending methods."""

    @patch('uuid.uuid4')
    @patch('multiprocessing.Queue')
    def test_send_command_single_subscriber(self, mock_queue_class, mock_uuid):
        """Test sending command to a single subscriber."""
        mock_uuid.return_value = "test-uuid-123"
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        command_name = "test_command"
        data = {"param1": "value1", "param2": 42}

        request_id = middleware.send_command(command_name, data)

        # Check return value
        assert request_id == "test-uuid-123"

        # Check that message was put in queue
        expected_message = {
            "name": command_name,
            "data": data,
            "requestId": "test-uuid-123",
            "isCommand": True
        }
        mock_queue.put.assert_called_once_with(expected_message)

    @patch('uuid.uuid4')
    @patch('multiprocessing.Queue')
    def test_send_command_multiple_subscribers(self, mock_queue_class, mock_uuid):
        """Test sending command to multiple subscribers."""
        mock_uuid.return_value = "multi-uuid-456"
        mock_queues = [MagicMock() for _ in range(2)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple subscribers
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()

        command_name = "multi_command"
        data = {"action": "start", "priority": "high"}

        request_id = middleware.send_command(command_name, data)

        # Check return value
        assert request_id == "multi-uuid-456"

        # Check all queues received the message
        expected_message = {
            "name": command_name,
            "data": data,
            "requestId": "multi-uuid-456",
            "isCommand": True
        }

        for mock_queue in mock_queues:
            mock_queue.put.assert_called_once_with(expected_message)

    def test_send_command_no_subscribers(self):
        """Test sending command when no subscribers exist."""
        middleware = Middleware()

        # Should not raise any exception and should return a UUID
        request_id = middleware.send_command("test", {"data": "value"})

        # Should return a valid UUID string
        assert isinstance(request_id, str)
        assert len(request_id) > 0

    @patch('multiprocessing.Queue')
    def test_send_command_answer_single_subscriber(self, mock_queue_class):
        """Test sending command answer to a single subscriber."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        command_name = "test_command"
        result = True
        data = {"response": "success", "code": 200}
        request_id = "req-123-456"

        middleware.send_command_answear(command_name, result, data, request_id)

        # Check that message was put in queue
        expected_message = {
            "name": command_name,
            "result": result,
            "data": data,
            "requestId": request_id,
            "isCommand": True
        }
        mock_queue.put.assert_called_once_with(expected_message)

    @patch('multiprocessing.Queue')
    def test_send_command_answer_multiple_subscribers(self, mock_queue_class):
        """Test sending command answer to multiple subscribers."""
        mock_queues = [MagicMock() for _ in range(2)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple subscribers
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()

        command_name = "answer_command"
        result = False
        data = {"error": "not found", "code": 404}
        request_id = "answer-req-789"

        middleware.send_command_answear(command_name, result, data, request_id)

        # Check all queues received the message
        expected_message = {
            "name": command_name,
            "result": result,
            "data": data,
            "requestId": request_id,
            "isCommand": True
        }

        for mock_queue in mock_queues:
            mock_queue.put.assert_called_once_with(expected_message)

    def test_send_command_answer_no_subscribers(self):
        """Test sending command answer when no subscribers exist."""
        middleware = Middleware()

        # Should not raise any exception
        middleware.send_command_answear(
            "test", True, {"data": "value"}, "req-123")

        # No queues to check, just ensure no exception was raised
        assert True


class TestMiddlewareEdgeCases:
    """Test edge cases and error conditions."""

    @patch('multiprocessing.Queue')
    def test_send_status_with_none_data(self, mock_queue_class):
        """Test sending status with None data."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        middleware.send_status("test_status", None)

        expected_message = {
            "name": "test_status",
            "data": None,
            "isCommand": False
        }
        mock_queue.put.assert_called_once_with(expected_message)

    @patch('multiprocessing.Queue')
    def test_send_status_with_complex_data(self, mock_queue_class):
        """Test sending status with complex nested data."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        complex_data = {
            "sensors": [
                {"id": 1, "value": 25.5, "active": True},
                {"id": 2, "value": 30.2, "active": False}
            ],
            "metadata": {
                "timestamp": 1234567890,
                "location": {"lat": 40.7128, "lng": -74.0060}
            }
        }

        middleware.send_status("complex_status", complex_data)

        expected_message = {
            "name": "complex_status",
            "data": complex_data,
            "isCommand": False
        }
        mock_queue.put.assert_called_once_with(expected_message)

    @patch('multiprocessing.Queue')
    def test_send_command_with_empty_data(self, mock_queue_class):
        """Test sending command with empty data."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        request_id = middleware.send_command("empty_command", {})

        # Check that message was put in queue with the returned request_id
        mock_queue.put.assert_called_once()
        call_args = mock_queue.put.call_args[0][0]
        assert call_args["name"] == "empty_command"
        assert call_args["data"] == {}
        assert call_args["requestId"] == request_id
        assert call_args["isCommand"] == True

    @patch('multiprocessing.Queue')
    def test_send_status_array_with_mixed_data_types(self, mock_queue_class):
        """Test sending status array with mixed data types."""
        mock_queue = MagicMock()
        mock_queue_class.return_value = mock_queue

        middleware = Middleware()
        middleware.add_new_middleware_listener()

        status_list = [
            {"statusName": "string_status", "data": "hello world"},
            {"statusName": "number_status", "data": 42},
            {"statusName": "boolean_status", "data": True},
            {"statusName": "list_status", "data": [1, 2, 3]},
            {"statusName": "dict_status", "data": {"key": "value"}}
        ]

        middleware.send_status_array(status_list)

        # Check that all 5 messages were sent
        assert mock_queue.put.call_count == 5

        # Check each message type
        expected_messages = [
            {"name": "string_status", "data": "hello world", "isCommand": False},
            {"name": "number_status", "data": 42, "isCommand": False},
            {"name": "boolean_status", "data": True, "isCommand": False},
            {"name": "list_status", "data": [1, 2, 3], "isCommand": False},
            {"name": "dict_status", "data": {"key": "value"}, "isCommand": False}
        ]

        calls = mock_queue.put.call_args_list
        for expected in expected_messages:
            assert any(
                call[0][0] == expected for call in calls), f"Expected message {expected} not found in calls"

    @patch('multiprocessing.Queue')
    def test_concurrent_operations(self, mock_queue_class):
        """Test that middleware can handle concurrent operations."""
        mock_queues = [MagicMock() for _ in range(2)]
        mock_queue_class.side_effect = mock_queues

        middleware = Middleware()

        # Add multiple subscribers
        middleware.add_new_middleware_listener()
        middleware.add_new_middleware_listener()

        # Simulate concurrent operations
        middleware.send_status("status1", {"id": 1})
        middleware.send_command("command1", {"action": "start"})
        middleware.send_status("status2", {"id": 2})
        middleware.send_command_answear(
            "command1", True, {"result": "success"}, "req-123")

        # Check that each queue received 4 messages
        for mock_queue in mock_queues:
            assert mock_queue.put.call_count == 4

            # Verify message types
            calls = mock_queue.put.call_args_list
            status_calls = [
                call for call in calls if not call[0][0]["isCommand"]]
            command_calls = [call for call in calls if call[0][0]["isCommand"]]

            assert len(status_calls) == 2  # 2 status messages
            assert len(command_calls) == 2  # 2 command messages
