from threading import Thread
from time import sleep
import asyncio

from .config_handler.config_handler import ConfigHandler
from support.logger import Logger

from middleware.middleware import ClientMiddleware

from .config_storage.config_storage import ConfigStorage

class ServiceManager:
    def __init__(self, middleware):
        self._logger = Logger()
        self._middleware = ClientMiddleware(middleware)

        self._status_saver = ConfigStorage(self._middleware)
        self._config_handler = ConfigHandler(self._middleware, self._status_saver)
        self._status_saver_thread = Thread(target = self.threaded_function, args = (10, ))
    
    def run(self):
        self._logger.info("Service Manager started")
        self._status_saver_thread.run()
    
    def threaded_function(self, args):
        while True:
            self._middleware.run_middleware_update()
            sleep(1)

    def join(self):
        self._status_saver_thread.join()
