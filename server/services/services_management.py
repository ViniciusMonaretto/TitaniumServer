from threading import Thread
from time import sleep
import asyncio

from services.gateway_manager.gateway_manager import GatewayManager
from services.alarm_manager.alarm_manager import AlarmManager
from services.sensor_data_storage.sensor_data_storage import SensorDataStorage
from services.report_generator.report_generator import ReportGenerator

from .config_handler.config_handler import ConfigHandler
from support.logger import Logger

from middleware.client_middleware import ClientMiddleware

from .config_storage.config_storage import ConfigStorage


class ServiceManager:
    def __init__(self, middleware):
        self._logger = Logger()
        self._middleware = ClientMiddleware(middleware)

        self._config_storage = ConfigStorage(self._middleware)
        self._sensor_data_storage = SensorDataStorage(self._middleware)
        self._alarm_manager = AlarmManager(
            self._middleware, self._config_storage)
        self._config_handler = ConfigHandler(
            self._middleware, self._config_storage, self._sensor_data_storage, self._alarm_manager)
        self._report_generator = ReportGenerator(
            self._middleware, self._sensor_data_storage, self._config_handler)
        self._gateway_manager = GatewayManager(
            self._middleware, self._config_handler)

        self._status_saver_thread = Thread(
            target=self.threaded_function, args=(10, ))

    def run(self):
        self._logger.info("Service Manager started")
        self._status_saver_thread.run()

    def threaded_function(self, args):
        while True:
            self._middleware.run_middleware_update()
            sleep(0.1)

    def join(self):
        self._status_saver_thread.join()
