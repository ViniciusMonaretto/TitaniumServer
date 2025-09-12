import threading
import time
from dataModules.gateway import GatewayStatus
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from modules.titanium_mqtt.translators.payload_model import MqttSystemModel
from services.gateway_manager.gateway_manager_commands import GatewayManagerCommands
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

        # Start a thread to send system status request after 5 seconds
        def delayed_system_status_request():
            time.sleep(5)
            self.send_system_status_request()

        threading.Thread(target=delayed_system_status_request,
                         daemon=True).start()

        self._logger.info("GatewayManager initialized")

    def initialize_commands(self):
        self._middleware.add_commands({
            GatewayManagerCommands.REQUEST_UPDATE_GATEWAYS: self.request_update_gateways_command,
            GatewayManagerCommands.GET_GATEWAYS: self.get_gateways_command
        })

    def send_system_status_request(self):
        self._middleware.send_command(MqttCommands.SYSTEM_STATUS_REQUEST, {})

    def request_update_gateways_command(self, command):
        self.send_system_status_request()
        self._middleware.send_command_answear(
            True, "sucess", command["requestId"])

    def get_gateways_command(self, command):
        self.send_gateways_status()
        self._middleware.send_command_answear(
            True, {}, command["requestId"])

    def initialize_system_callbacks(self):
        self._gateway_status_subscriber = StatuSubscribers(
            self.update_gateway_status_callback, "gateway-status-*")
        self._middleware.add_subscribe_to_status(
            self._gateway_status_subscriber, "gateway-status-*")

    def send_gateways_status(self):
        gateways_array = [self._gateways[gateway_name].to_json()
                          for gateway_name in self._gateways.keys()]
        self._middleware.send_status(
            "gateway-statusupdate-*", gateways_array)

    def update_gateway_status_callback(self, status_info):
        system_status: MqttSystemModel = status_info["data"]

        gateway_status: GatewayStatus = GatewayStatus()
        gateway_status.name = system_status.gateway.name
        gateway_status.ip = system_status.gateway.ip
        gateway_status.uptime = system_status.gateway.uptime

        self._gateways[system_status.gateway.name] = gateway_status
        self._config_handler.update_calibration_from_gateway_status(
            system_status.panels)
        self.send_gateways_status()
