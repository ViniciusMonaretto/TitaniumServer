from threading import Thread
from time import sleep
import asyncio

from middleware.middleware import ClientMiddleware

from .status_saver.status_saver import StatusSaver

class ServiceManager:
    def __init__(self, middleware):
        self._middleware = ClientMiddleware(middleware)

        self._status_saver = StatusSaver(self._middleware)
        self._status_saver_thread = Thread(target = self.threaded_function, args = (10, ))
    
    def run(self):
        self._status_saver_thread.run()
    
    def threaded_function(self, args):
        while True:
            self._middleware.run_middleware_update()
            sleep(1)

    def join(self):
        self._status_saver_thread.join()
