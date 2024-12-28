from threading import Thread
from time import sleep
import asyncio

from middleware.middleware import ClientMiddleware

from .status_saver.status_saver import SatatusSaver

class ModulesManager:
    def __init__(self, middleware):
        self._status_saver = SatatusSaver(middleware)
        self._status_saver_thread = Thread(target = self.threaded_function, args = (10, ))
        self._middleware = ClientMiddleware(middleware)

    def threaded_function(self, args):
        self._middleware.run_status_update()

    def join(self):
        self._status_saver_thread.join()
