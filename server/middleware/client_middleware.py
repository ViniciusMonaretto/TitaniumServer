from collections.abc import Callable
import multiprocessing
import threading
from time import sleep
from typing import Any
from middleware.middleware import Middleware
from middleware.data_converter.data_converter import DataConverter
from middleware.subscriber_interface import SubscriberInterface
from middleware.subscriber_manager import SubscriberManager
from support.logger import Logger


class ClientMiddleware:
    def __init__(self, middleware: Middleware, name: str):
        self._logger = Logger()
        self._lock = threading.Lock()
        self._data_converter = DataConverter()
        self._subscribers: dict[str, SubscriberManager] = {}
        self._transfer_queue:  multiprocessing.Queue = middleware.add_new_middleware_listener()
        self._request_queue: dict[str, tuple[Callable, Callable]] = {}
        self._global_middleware = middleware
        self._commands_available: dict[str, Callable] = {}
        self._name = name
        
    @staticmethod
    def get_calibrate_topic(gateway, topic, indicator):
        return gateway + '-' + topic + "-" + indicator + "calibrate"

    @staticmethod
    def get_status_topic(gateway, topic, indicator):
        return gateway + '-' + topic + "-" + indicator

    def add_commands(self, commands_available: dict[str, Callable[[dict], None]]):
        self._commands_available = self._commands_available | commands_available

    def add_subscribe_to_status(self, subscriber: SubscriberInterface, status_name):
        self._lock.acquire()
        if (not (status_name in self._subscribers)):
            self._subscribers[status_name] = SubscriberManager(subscriber)

        self._subscribers[status_name].add_subscriber(subscriber)
        self._lock.release()

    def remove_subscribe_from_status(self, subscriber, status_name):
        self._lock.acquire()
        subscriber_id = subscriber.get_id()
        if (not (status_name in self._subscribers)):
            self._logger.info(
                f"Middleware::add_subscribe_from_status-> Error, subscriber {subscriber_id} non existant")
            return

        self._subscribers[status_name].remove_subscriber(subscriber_id)
        self._lock.release()

    def send_command(self, command_name, data, callback_handler=None, error_handler=None):
        self._request_queue[self._global_middleware.send_command(
            command_name, data)] = (callback_handler, error_handler)

    def send_command_answear(self, result, data, request_id):
        self._global_middleware.send_command_answear(
            "", result, data, request_id)

    def command_update(self, new_command):
        command_name = new_command["name"]
        if command_name in self._commands_available:
            self._commands_available[command_name](new_command)

    def _check_if_subscribed(self, subscriber_status_name: str, status_name: str):
        sub_info = subscriber_status_name.split('-')
        status_info = status_name.split('-')

        gateway_match = (sub_info[0] == '*') or (sub_info[0] == status_info[0])
        topic_match = (sub_info[1] == '*') or (sub_info[1] == status_info[1])
        indicator_match = (
            sub_info[2] == '*') or (sub_info[2] == status_info[2])
        return gateway_match and topic_match and indicator_match

    def send_status(self, topic: str, new_status):
        self._global_middleware.send_status(topic, new_status)

    def send_status_array(self, status_list: list[Any]):
        self._global_middleware.send_status_array(status_list)

############################################################################################################
################################# Middleware Update System #################################################

    def run_middleware_update(self):
        while (not self._transfer_queue.empty()):
            new_info = self._transfer_queue.get()
            if new_info["isCommand"]:
                self._command_update(new_info)
            else:
                self._status_update(new_info)
            # sleep(0.1)

    def _command_update(self, new_command):
        if new_command["requestId"] in self._request_queue and new_command["name"] == "":
            command_id = new_command["requestId"]
            callbacks = self._request_queue[command_id]
            if new_command["result"]:
                if callbacks[0]:
                    callbacks[0](new_command)
            else:
                if callbacks[1]:
                    callbacks[1](new_command)
            del self._request_queue[command_id]
        else:
            self.command_update(new_command)

    def _status_update(self, new_status):
        status_name = new_status["name"]
        data = new_status["data"]

        generated_status: list[dict[str, Any]] = self._data_converter.convert_data(
            status_name.split('-')[1], data)
        for subscriber_status_name, subscriber in self._subscribers.items():
            if self._check_if_subscribed(subscriber_status_name, status_name):
                subscriber.send_status(status_name, data)
            if generated_status:
                for status_gen in generated_status:
                    if self._check_if_subscribed(subscriber_status_name, status_gen["name"]):
                        subscriber.send_status(
                            status_gen["name"], status_gen["value"])
