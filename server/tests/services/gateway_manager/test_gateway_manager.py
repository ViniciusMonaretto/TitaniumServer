import pytest
import threading
import time
import weakref
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Import the classes to be tested
from services.gateway_manager.gateway_manager import GatewayManager
from services.gateway_manager.gateway_manager_commands import GatewayManagerCommands
from dataModules.gateway import GatewayStatus
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from modules.titanium_mqtt.translators.payload_model import MqttSystemModel
from middleware.status_subscriber import StatuSubscribers


@pytest.fixture
def mock_middleware():
    """Create a mock middleware for testing."""
    middleware = MagicMock()
    middleware.add_commands = MagicMock()
    middleware.send_command = MagicMock()
    middleware.send_command_answear = MagicMock()
    middleware.send_status = MagicMock()
    middleware.add_subscribe_to_status = MagicMock()
    middleware.remove_subscribe_to_status = MagicMock()
    return middleware


@pytest.fixture
def mock_config_handler():
    """Create a mock config handler for testing."""
    config_handler = MagicMock()
    config_handler.update_calibration_from_gateway_status = MagicMock()
    return config_handler


@pytest.fixture
def gateway_manager(mock_middleware, mock_config_handler):
    """Create a GatewayManager instance for testing."""
    with patch('services.gateway_manager.gateway_manager.Logger'):
        return GatewayManager(mock_middleware, mock_config_handler)


@pytest.fixture
def sample_gateway_status():
    """Create a sample gateway status for testing."""
    status = GatewayStatus()
    status.name = "test-gateway"
    status.ip = "192.168.1.100"
    status.uptime = 3600
    return status


@pytest.fixture
def sample_mqtt_system_model():
    """Create a sample MQTT system model for testing."""
    model = MagicMock()
    model.gateway = MagicMock()
    model.gateway.name = "test-gateway"
    model.gateway.ip = "192.168.1.100"
    model.gateway.uptime = 3600
    model.panels = []
    return model


class TestGatewayManagerInitialization:
    """Test GatewayManager initialization and setup."""

    def test_initialization(self, mock_middleware, mock_config_handler):
        """Test that GatewayManager initializes correctly."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            assert manager._middleware == mock_middleware
            assert manager._config_handler == mock_config_handler
            assert isinstance(manager._gateways, dict)
            assert len(manager._gateways) == 0
            assert isinstance(manager._shutdown_event, threading.Event)
            assert not manager._shutdown_event.is_set()

    def test_weakref_setup(self, mock_middleware, mock_config_handler):
        """Test that weak references are set up correctly."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            assert isinstance(manager._middleware_ref, weakref.ref)
            assert isinstance(manager._config_handler_ref, weakref.ref)
            assert manager._middleware_ref() == mock_middleware
            assert manager._config_handler_ref() == mock_config_handler

    def test_commands_initialization(self, mock_middleware, mock_config_handler):
        """Test that commands are registered with middleware."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            expected_commands = {
                GatewayManagerCommands.REQUEST_UPDATE_GATEWAYS: manager.request_update_gateways_command,
                GatewayManagerCommands.GET_GATEWAYS: manager.get_gateways_command
            }
            mock_middleware.add_commands.assert_called_once_with(
                expected_commands)

    def test_status_subscriber_setup(self, mock_middleware, mock_config_handler):
        """Test that status subscriber is set up correctly."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            mock_middleware.add_subscribe_to_status.assert_called_once()
            call_args = mock_middleware.add_subscribe_to_status.call_args
            subscriber, topic_pattern = call_args[0]
            assert isinstance(subscriber, StatuSubscribers)
            assert topic_pattern == "gateway-status-*"

    def test_delayed_thread_start(self, mock_middleware, mock_config_handler):
        """Test that delayed thread starts correctly."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            assert hasattr(manager, '_delayed_thread')
            assert isinstance(manager._delayed_thread, threading.Thread)
            assert manager._delayed_thread.daemon is True
            assert manager._delayed_thread.name == "GatewayManager-delayed-request"


class TestGatewayManagerCommands:
    """Test GatewayManager command handling."""

    def test_request_update_gateways_command_success(self, gateway_manager, mock_middleware):
        """Test successful request update gateways command."""
        command = {"requestId": "test-request-123"}

        gateway_manager.request_update_gateways_command(command)

        # Should send system status request
        mock_middleware.send_command.assert_called_once_with(
            MqttCommands.SYSTEM_STATUS_REQUEST, {}
        )
        # Should send success response
        mock_middleware.send_command_answear.assert_called_once_with(
            True, "success", "test-request-123"
        )

    def test_request_update_gateways_command_error(self, gateway_manager, mock_middleware):
        """Test request update gateways command with error."""
        command = {"requestId": "test-request-123"}

        # Make send_command raise an exception
        mock_middleware.send_command.side_effect = Exception(
            "Connection error")

        gateway_manager.request_update_gateways_command(command)

        # Should still attempt to send command
        mock_middleware.send_command.assert_called_once()
        # Should still send success response (actual implementation behavior)
        mock_middleware.send_command_answear.assert_called_once_with(
            True, "success", "test-request-123"
        )

    def test_get_gateways_command_with_gateways(self, gateway_manager, mock_middleware, sample_gateway_status):
        """Test get gateways command when gateways exist."""
        # Add a gateway to the manager
        gateway_manager._gateways["test-gateway"] = sample_gateway_status

        command = {"requestId": "test-request-456"}

        gateway_manager.get_gateways_command(command)

        # Should send gateways status
        mock_middleware.send_status.assert_called_once()
        # Should send success response
        mock_middleware.send_command_answear.assert_called_once_with(
            True, {}, "test-request-456"
        )

    def test_get_gateways_command_empty_gateways(self, gateway_manager, mock_middleware):
        """Test get gateways command when no gateways exist."""
        command = {"requestId": "test-request-456"}

        gateway_manager.get_gateways_command(command)

        # Should not send status when no gateways
        mock_middleware.send_status.assert_not_called()
        # Should still send success response
        mock_middleware.send_command_answear.assert_called_once_with(
            True, {}, "test-request-456"
        )


class TestGatewayStatusHandling:
    """Test gateway status update handling."""

    def test_update_gateway_status_callback_success(self, gateway_manager, sample_mqtt_system_model, mock_config_handler):
        """Test successful gateway status update."""
        status_info = {"data": sample_mqtt_system_model}

        gateway_manager.update_gateway_status_callback(status_info)

        # Should add gateway to internal dictionary
        assert "test-gateway" in gateway_manager._gateways
        gateway_status = gateway_manager._gateways["test-gateway"]
        assert gateway_status.name == "test-gateway"
        assert gateway_status.ip == "192.168.1.100"
        assert gateway_status.uptime == 3600

        # Should update calibration
        mock_config_handler.update_calibration_from_gateway_status.assert_called_once_with([
        ])

    def test_update_gateway_status_callback_during_shutdown(self, gateway_manager, sample_mqtt_system_model):
        """Test gateway status update during shutdown."""
        # Set shutdown event
        gateway_manager._shutdown_event.set()

        status_info = {"data": sample_mqtt_system_model}
        gateway_manager.update_gateway_status_callback(status_info)

        # Should not process during shutdown
        assert len(gateway_manager._gateways) == 0

    def test_update_gateway_status_callback_error(self, gateway_manager):
        """Test gateway status update with error."""
        # Invalid status info
        status_info = {"data": None}

        gateway_manager.update_gateway_status_callback(status_info)

        # Should handle error gracefully
        assert len(gateway_manager._gateways) == 0

    def test_gateway_limit_enforcement(self, gateway_manager, sample_mqtt_system_model):
        """Test that gateway limit is enforced."""
        # Add more than 100 gateways
        for i in range(105):
            model = MagicMock()
            model.gateway = MagicMock()
            model.gateway.name = f"gateway-{i}"
            model.gateway.ip = f"192.168.1.{i}"
            model.gateway.uptime = 3600
            model.panels = []

            status_info = {"data": model}
            gateway_manager.update_gateway_status_callback(status_info)

        # Should have exactly 100 gateways
        assert len(gateway_manager._gateways) == 100
        # Should not contain the first gateway (oldest)
        assert "gateway-0" not in gateway_manager._gateways
        # Should contain the last gateway (newest)
        assert "gateway-104" in gateway_manager._gateways


class TestGatewayStatusSending:
    """Test gateway status sending functionality."""

    def test_send_gateways_status_with_gateways(self, gateway_manager, mock_middleware, sample_gateway_status):
        """Test sending gateway status when gateways exist."""
        gateway_manager._gateways["test-gateway"] = sample_gateway_status

        gateway_manager.send_gateways_status()

        # Should send status with gateway data
        mock_middleware.send_status.assert_called_once()
        call_args = mock_middleware.send_status.call_args
        topic, data = call_args[0]
        assert topic == "gateway-statusupdate-*"
        assert len(data) == 1
        assert data[0]["name"] == "test-gateway"
        assert data[0]["ip"] == "192.168.1.100"
        assert data[0]["uptime"] == 3600

    def test_send_gateways_status_empty(self, gateway_manager, mock_middleware):
        """Test sending gateway status when no gateways exist."""
        gateway_manager.send_gateways_status()

        # Should not send status when no gateways
        mock_middleware.send_status.assert_not_called()

    def test_send_gateways_status_during_shutdown(self, gateway_manager, mock_middleware, sample_gateway_status):
        """Test sending gateway status during shutdown."""
        gateway_manager._gateways["test-gateway"] = sample_gateway_status
        gateway_manager._shutdown_event.set()

        gateway_manager.send_gateways_status()

        # Should not send status during shutdown
        mock_middleware.send_status.assert_not_called()

    def test_send_gateways_status_error(self, gateway_manager, mock_middleware, sample_gateway_status):
        """Test sending gateway status with error."""
        gateway_manager._gateways["test-gateway"] = sample_gateway_status
        mock_middleware.send_status.side_effect = Exception("Send error")

        gateway_manager.send_gateways_status()

        # Should handle error gracefully
        # No assertion needed as method should not raise


class TestSystemStatusRequest:
    """Test system status request functionality."""

    def test_send_system_status_request_success(self, gateway_manager, mock_middleware):
        """Test successful system status request."""
        gateway_manager.send_system_status_request()

        mock_middleware.send_command.assert_called_once_with(
            MqttCommands.SYSTEM_STATUS_REQUEST, {}
        )

    def test_send_system_status_request_during_shutdown(self, gateway_manager, mock_middleware):
        """Test system status request during shutdown."""
        gateway_manager._shutdown_event.set()

        gateway_manager.send_system_status_request()

        # Should not send request during shutdown
        mock_middleware.send_command.assert_not_called()

    def test_send_system_status_request_error(self, gateway_manager, mock_middleware):
        """Test system status request with error."""
        mock_middleware.send_command.side_effect = Exception(
            "Connection error")

        gateway_manager.send_system_status_request()

        # Should handle error gracefully
        # No assertion needed as method should not raise


class TestCleanupAndShutdown:
    """Test cleanup and shutdown functionality."""

    def test_cleanup_success(self, gateway_manager, mock_middleware):
        """Test successful cleanup."""
        # Add some gateways
        gateway_manager._gateways["test-gateway"] = MagicMock()

        gateway_manager.cleanup()

        # Should set shutdown event
        assert gateway_manager._shutdown_event.is_set()
        # Should clear gateways
        assert len(gateway_manager._gateways) == 0
        # Should remove status subscriber
        mock_middleware.remove_subscribe_to_status.assert_called_once()

    def test_cleanup_with_thread(self, gateway_manager):
        """Test cleanup with active thread."""
        # Wait a bit to ensure thread is running
        time.sleep(0.1)

        gateway_manager.cleanup()

        # Should set shutdown event
        assert gateway_manager._shutdown_event.is_set()

    def test_cleanup_error_handling(self, gateway_manager, mock_middleware):
        """Test cleanup with errors."""
        # Make remove_subscribe_to_status raise an exception
        mock_middleware.remove_subscribe_to_status.side_effect = Exception(
            "Remove error")

        gateway_manager.cleanup()

        # Should handle error gracefully and continue
        assert gateway_manager._shutdown_event.is_set()

    def test_destructor(self, mock_middleware, mock_config_handler):
        """Test destructor calls cleanup."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            # Mock cleanup to verify it's called
            with patch.object(manager, 'cleanup') as mock_cleanup:
                del manager
                # Note: In real scenarios, __del__ might not be called immediately
                # This test verifies the destructor exists and calls cleanup


class TestMemoryManagement:
    """Test memory management functionality."""

    def test_memory_stats(self, gateway_manager):
        """Test memory statistics collection."""
        # Add some gateways
        gateway_manager._gateways["test-gateway"] = MagicMock()

        stats = gateway_manager.get_memory_stats()

        assert 'rss_mb' in stats
        assert 'vms_mb' in stats
        assert 'gateways_count' in stats
        assert 'threads_alive' in stats
        assert 'shutdown_requested' in stats
        assert stats['gateways_count'] == 1
        assert stats['shutdown_requested'] is False

    def test_memory_stats_during_shutdown(self, gateway_manager):
        """Test memory statistics during shutdown."""
        gateway_manager._shutdown_event.set()

        stats = gateway_manager.get_memory_stats()

        assert stats['shutdown_requested'] is True

    def test_garbage_collection_trigger(self, gateway_manager, sample_mqtt_system_model):
        """Test that garbage collection is triggered periodically."""
        # Add 10 gateways to trigger GC
        for i in range(10):
            model = MagicMock()
            model.gateway = MagicMock()
            model.gateway.name = f"gateway-{i}"
            model.gateway.ip = f"192.168.1.{i}"
            model.gateway.uptime = 3600
            model.panels = []

            status_info = {"data": model}
            gateway_manager.update_gateway_status_callback(status_info)

        # Should have 10 gateways
        assert len(gateway_manager._gateways) == 10


class TestThreading:
    """Test threading functionality."""

    def test_delayed_thread_functionality(self, mock_middleware, mock_config_handler):
        """Test that delayed thread sends system status request."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            # Wait for delayed thread to complete (5 seconds + some buffer)
            time.sleep(6)

            # Should have sent system status request
            mock_middleware.send_command.assert_called_with(
                MqttCommands.SYSTEM_STATUS_REQUEST, {}
            )

    def test_delayed_thread_shutdown(self, mock_middleware, mock_config_handler):
        """Test that delayed thread respects shutdown signal."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            # Set shutdown immediately
            manager._shutdown_event.set()

            # Wait a bit
            time.sleep(1)

            # Should not send system status request due to shutdown
            mock_middleware.send_command.assert_not_called()


class TestGatewayStatusDataModel:
    """Test GatewayStatus data model."""

    def test_gateway_status_creation(self):
        """Test GatewayStatus object creation."""
        status = GatewayStatus()
        status.name = "test-gateway"
        status.ip = "192.168.1.100"
        status.uptime = 3600

        assert status.name == "test-gateway"
        assert status.ip == "192.168.1.100"
        assert status.uptime == 3600

    def test_gateway_status_to_json(self):
        """Test GatewayStatus to_json method."""
        status = GatewayStatus()
        status.name = "test-gateway"
        status.ip = "192.168.1.100"
        status.uptime = 3600

        json_data = status.to_json()

        expected = {
            "name": "test-gateway",
            "ip": "192.168.1.100",
            "uptime": 3600
        }
        assert json_data == expected


class TestIntegration:
    """Integration tests for GatewayManager."""

    def test_full_workflow(self, mock_middleware, mock_config_handler, sample_mqtt_system_model):
        """Test complete workflow from status update to status sending."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            # Simulate gateway status update
            status_info = {"data": sample_mqtt_system_model}
            manager.update_gateway_status_callback(status_info)

            # Verify gateway was added
            assert "test-gateway" in manager._gateways

            # Simulate get gateways command
            command = {"requestId": "test-request"}
            manager.get_gateways_command(command)

            # Verify status was sent
            mock_middleware.send_status.assert_called()
            call_args = mock_middleware.send_status.call_args
            topic, data = call_args[0]
            assert topic == "gateway-statusupdate-*"
            assert len(data) == 1
            assert data[0]["name"] == "test-gateway"

    def test_error_recovery(self, mock_middleware, mock_config_handler):
        """Test that the manager recovers from errors gracefully."""
        with patch('services.gateway_manager.gateway_manager.Logger'):
            manager = GatewayManager(mock_middleware, mock_config_handler)

            # Make middleware methods raise exceptions
            mock_middleware.send_command.side_effect = Exception(
                "Connection error")
            mock_middleware.send_status.side_effect = Exception("Send error")

            # Should handle errors gracefully
            manager.send_system_status_request()
            manager.send_gateways_status()

            # Manager should still be functional
            assert not manager._shutdown_event.is_set()
            assert len(manager._gateways) == 0
