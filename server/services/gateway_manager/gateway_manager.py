from dataModules.gateway import GatewayStatus
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from modules.titanium_mqtt.translators.payload_model import MqttSystemModel
from services.config_handler.config_handler import ConfigHandler
from support.logger import Logger
from middleware.client_middleware import ClientMiddleware
from middleware.status_subscriber import StatuSubscribers
from ..service_interface import ServiceInterface


class GatewayManager(ServiceInterface):

    _gateway_status_subscriber: StatuSubscribers
    _gateways: dict[str, GatewayStatus]

    def __init__(self,
                 middleware: ClientMiddleware,
                 config_handler: ConfigHandler):
        self._logger = Logger()
        self._middleware = middleware
        self._config_handler = config_handler
        self._gateways = {}

        self.initialize_commands()
        self.initialize_system_callbacks()

        self._middleware.send_command(MqttCommands.STATUS_REQUEST, {})

        self._logger.info("GatewayManager initialized")

    def initialize_system_callbacks(self):
        self._gateway_status_subscriber = StatuSubscribers(
            self.update_gateway_status_callback, "gateway-status-*")
        self._middleware.add_subscribe_to_status(
            self._gateway_status_subscriber, "gateway-status-*")

    def initialize_commands(self):
        pass

    def send_gateway_status(self, gateway_status: GatewayStatus):
        self._middleware.send_status(
            "gateway-statusupdate-*", gateway_status)

    def update_gateway_status_callback(self, status_info):
        system_status: MqttSystemModel = status_info["data"]

        gateway_status: GatewayStatus = GatewayStatus()
        gateway_status.name = system_status.gateway.name
        gateway_status.ip = system_status.gateway.ip
        gateway_status.uptime = system_status.gateway.uptime

        self._gateways[system_status.gateway.name] = gateway_status
        self._config_handler.update_calibration_from_gateway_status(
            system_status.panels)
