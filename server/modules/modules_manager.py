from threading import Thread
from time import sleep
import asyncio

from support.logger import Logger
from .titanium_esp_protocol_http_client.titanium_esp_protocol_http_client import TitaniumEspProtocol
from .titanium_server.titanium_server import TitaniumServer
from .titanium_mqtt.mqtt import TitaniumMqtt

class ModulesManager:
    def __init__(self, middleware):
        self._logger = Logger()
        self._titanium_mqtt = TitaniumMqtt(middleware)
        self._middleware = middleware

    def threaded_function(self, args):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.m_TitaniumServer.run())
        self.loop.close()
    
    def run(self):
        self._logger.info("Modules Manager start")
        self._titanium_mqtt.run()

    def join(self):
        self._titanium_mqtt.stop()

