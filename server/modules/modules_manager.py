from threading import Thread
from time import sleep
from middleware.client_middleware import ClientMiddleware
from support.logger import Logger
from .titanium_mqtt.mqtt import TitaniumMqtt

class ModulesManager:
    _finish = False
    def __init__(self, middleware):
        self._logger = Logger()
        self._client_middleware = ClientMiddleware(middleware)
        self._titanium_mqtt = TitaniumMqtt(self._client_middleware)
        self._middleware = middleware
        self._command_handler_thread = Thread(target = self.threaded_function)
    
    def run(self):
        self._logger.info("Modules Manager start")
        self._titanium_mqtt.run()
        self._command_handler_thread.start()

    def join(self):
        self._finish = True
        self._titanium_mqtt.stop()
        self._command_handler_thread.join()

    def threaded_function(self):
        while not self._finish:
            self._client_middleware.run_middleware_update()
            sleep(0.1)

