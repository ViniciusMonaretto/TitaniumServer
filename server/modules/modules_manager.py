from threading import Thread
from time import sleep
import asyncio
from .titanium_esp_protocol_http_client.titanium_esp_protocol_http_client import TitaniumEspProtocol
from .titanium_server.titanium_server import TitaniumServer
from .titanium_mqtt.mqtt import TitaniumMqtt

class ModulesManager:
    def __init__(self, middleware):
        self.m_TitaniumServer = TitaniumServer(middleware)
        self.m_TitaniumServerThread = Thread(target = self.threaded_function, args = (10, ))
        self._titanium_mqtt = TitaniumMqtt(middleware)
        self._middleware = middleware

    def threaded_function(self, args):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.m_TitaniumServer.run())
        self.loop.close()
    
    def run(self):
        self.m_TitaniumServerThread.start()
        self._titanium_mqtt.run()

    def join(self):
        self.m_TitaniumServerThread.join()

