import threading
import time
import gc
import weakref
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
    _delayed_thread: threading.Thread
    _shutdown_event: threading.Event

    def __init__(self,
                 middleware: ClientMiddleware,
                 config_handler: ConfigHandler):
        self._logger = Logger()
        self._middleware = middleware
        self._config_handler = config_handler
        self._gateways = {}
        self._shutdown_event = threading.Event()
        
        # Use weakref para evitar referências circulares
        self._middleware_ref = weakref.ref(middleware)
        self._config_handler_ref = weakref.ref(config_handler)

        self.initialize_commands()
        self.initialize_system_callbacks()

        # Start a thread to send system status request after 5 seconds
        def delayed_system_status_request():
            try:
                # Aguarda 5 segundos ou sinal de shutdown
                if self._shutdown_event.wait(5):
                    return  # Shutdown solicitado
                
                # Envia request apenas se não foi solicitado shutdown
                if not self._shutdown_event.is_set():
                    self.send_system_status_request()
            except Exception as e:
                self._logger.error(f"Erro no delayed_system_status_request: {e}")
            finally:
                # Força garbage collection após o thread
                gc.collect()

        self._delayed_thread = threading.Thread(
            target=delayed_system_status_request,
            daemon=True,
            name="GatewayManager-delayed-request"
        )
        self._delayed_thread.start()

        self._logger.info("GatewayManager initialized")

    def __del__(self):
        """Destructor para limpeza"""
        try:
            self.cleanup()
        except:
            pass  # Ignora erros no destructor

    def cleanup(self):
        """Limpa recursos e para threads"""
        try:
            # Sinaliza shutdown
            self._shutdown_event.set()
            
            # Aguarda thread terminar (com timeout)
            if hasattr(self, '_delayed_thread') and self._delayed_thread.is_alive():
                self._delayed_thread.join(timeout=2)
            
            # Limpa callbacks
            if hasattr(self, '_gateway_status_subscriber'):
                try:
                    middleware = self._middleware_ref()
                    if middleware:
                        middleware.remove_subscribe_to_status(self._gateway_status_subscriber)
                except:
                    pass
            
            # Limpa dicionário de gateways
            if hasattr(self, '_gateways'):
                self._gateways.clear()
            
            # Força garbage collection
            gc.collect()
            
            self._logger.info("GatewayManager cleanup completed")
        except Exception as e:
            self._logger.error(f"Erro durante cleanup: {e}")

    def initialize_commands(self):
        middleware = self._middleware_ref()
        if middleware:
            middleware.add_commands({
                GatewayManagerCommands.REQUEST_UPDATE_GATEWAYS: self.request_update_gateways_command,
                GatewayManagerCommands.GET_GATEWAYS: self.get_gateways_command
            })

    def send_system_status_request(self):
        try:
            middleware = self._middleware_ref()
            if middleware and not self._shutdown_event.is_set():
                middleware.send_command(MqttCommands.SYSTEM_STATUS_REQUEST, {})
        except Exception as e:
            self._logger.error(f"Erro ao enviar system status request: {e}")

    def request_update_gateways_command(self, command):
        try:
            self.send_system_status_request()
            middleware = self._middleware_ref()
            if middleware:
                middleware.send_command_answear(
                    True, "success", command["requestId"])
        except Exception as e:
            self._logger.error(f"Erro no request_update_gateways_command: {e}")

    def get_gateways_command(self, command):
        try:
            self.send_gateways_status()
            middleware = self._middleware_ref()
            if middleware:
                middleware.send_command_answear(
                    True, {}, command["requestId"])
        except Exception as e:
            self._logger.error(f"Erro no get_gateways_command: {e}")

    def initialize_system_callbacks(self):
        try:
            middleware = self._middleware_ref()
            if middleware:
                self._gateway_status_subscriber = StatuSubscribers(
                    self.update_gateway_status_callback, "gateway-status-*")
                middleware.add_subscribe_to_status(
                    self._gateway_status_subscriber, "gateway-status-*")
        except Exception as e:
            self._logger.error(f"Erro ao inicializar callbacks: {e}")

    def send_gateways_status(self):
        try:
            if not self._gateways:
                return
                
            gateways_array = [self._gateways[gateway_name].to_json()
                              for gateway_name in self._gateways.keys()]
            
            middleware = self._middleware_ref()
            if middleware and not self._shutdown_event.is_set():
                middleware.send_status(
                    "gateway-statusupdate-*", gateways_array)
        except Exception as e:
            self._logger.error(f"Erro ao enviar status dos gateways: {e}")

    def update_gateway_status_callback(self, status_info):
        try:
            if self._shutdown_event.is_set():
                return
                
            system_status: MqttSystemModel = status_info["data"]

            gateway_status: GatewayStatus = GatewayStatus()
            gateway_status.name = system_status.gateway.name
            gateway_status.ip = system_status.gateway.ip
            gateway_status.uptime = system_status.gateway.uptime

            self._gateways[system_status.gateway.name] = gateway_status
            
            # Limita o tamanho do dicionário para evitar crescimento indefinido
            if len(self._gateways) > 100:  # Limite arbitrário
                # Remove entradas mais antigas (simples implementação)
                oldest_key = next(iter(self._gateways))
                del self._gateways[oldest_key]
                self._logger.warning(f"Removido gateway antigo: {oldest_key}")
            
            config_handler = self._config_handler_ref()
            if config_handler:
                config_handler.update_calibration_from_gateway_status(
                    system_status.panels)
            
            self.send_gateways_status()
            
            # Força garbage collection periodicamente
            if len(self._gateways) % 10 == 0:
                gc.collect()
                
        except Exception as e:
            self._logger.error(f"Erro no update_gateway_status_callback: {e}")

    def get_memory_stats(self):
        """Retorna estatísticas de memória para debugging"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'gateways_count': len(self._gateways),
            'threads_alive': threading.active_count(),
            'shutdown_requested': self._shutdown_event.is_set()
        }
