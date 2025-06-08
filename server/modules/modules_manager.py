from support.logger import Logger
from .titanium_mqtt.mqtt import TitaniumMqtt

class ModulesManager:
    def __init__(self, middleware):
        self._logger = Logger()
        self._titanium_mqtt = TitaniumMqtt(middleware)
        self._middleware = middleware
    
    def run(self):
        self._logger.info("Modules Manager start")
        self._titanium_mqtt.run()

    def join(self):
        self._titanium_mqtt.stop()

