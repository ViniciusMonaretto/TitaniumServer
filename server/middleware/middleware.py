import threading
import multiprocessing
import uuid
from collections.abc import Callable
from support.logger import Logger
from .data_converter.data_converter import DataConverter
from .subscriber_interface import SubscriberInterface

class SubscriberManager:
    def __init__(self, status):
        self._status_name = status._status
        self._subscriber_map = {}
    
    def add_subscriber(self, subscriber: SubscriberInterface):
        self._subscriber_map[subscriber.get_id()] = subscriber

    def remove_subscriber(self, subscriber_id):
        if(not (subscriber_id in self._subscriber_map)):
            print(f"Middleware::add_subscribe_from_status-> Error, subscriber {subscriber_id} non subscribing {self._status_name}")
            return

        del self._subscriber_map[subscriber_id]

    def send_status(self, status_name, data):
        for subscriber_id in self._subscriber_map:
            subscriber = self._subscriber_map[subscriber_id]
            subscriber.on_status(status_name, data, self._status_name)

class Middleware:
    def __init__(self):
        self._logger = Logger()
        self._subscriber_queues = []
        self._request_queues = []

    def add_new_middleware_listener(self):
        queue = multiprocessing.Queue()
        self._subscriber_queues.append(queue)
        return queue
    
    def add_new_request_listener(self):
        queue = multiprocessing.Queue()
        self._request_queues.append(queue)
        return queue

    def send_status(self, status_name, data):
        for queue in self._subscriber_queues:
            queue.put({"name": status_name, "data": data, "isCommand": False})
    
    def send_command(self, command_name, data):
        request_id = str(uuid.uuid4())
        for queue in self._subscriber_queues:
            queue.put({"name": command_name, "data": data, "requestId": request_id, "isCommand": True})
        
        return request_id
    
    def send_command_answear(self, command_name, result, data, request_id):
        for queue in self._subscriber_queues:
            queue.put({"name": command_name, "result": result, "data": data, "requestId": request_id, "isCommand": True})

class ClientMiddleware:
    def __init__(self, middleware: Middleware):
        self._logger = Logger()
        self._lock = threading.Lock()
        self._data_converter = DataConverter()
        self._subscribers: dict[str, SubscriberManager] = {}
        self._transfer_queue:  multiprocessing.Queue = middleware.add_new_middleware_listener()
        self._request_queue: dict[str, tuple[Callable, Callable]] = {}
        self._global_middleware = middleware
        self._commands_available: dict[str, Callable] = {}
    
    def add_commands(self, commands_available: dict[str, Callable[[dict], None]]):
        self._commands_available = self._commands_available | commands_available

    def add_subscribe_to_status(self, subscriber: SubscriberInterface, status_name):
        self._lock.acquire()
        if(not (status_name in self._subscribers)):
            self._subscribers[status_name] = SubscriberManager(subscriber)
        
        self._subscribers[status_name].add_subscriber(subscriber)
        self._lock.release()

    def remove_subscribe_from_status(self, subscriber, status_name):
        self._lock.acquire()
        subscriber_id = subscriber.get_id()
        if(not (status_name in self._subscribers)):
            self._logger.info(f"Middleware::add_subscribe_from_status-> Error, subscriber {subscriber_id} non existant")
            return
        
        self._subscribers[status_name].remove_subscriber(subscriber_id)
        self._lock.release()

    def send_command(self, command_name, data, callback_handler = None, error_handler = None):
        self._request_queue[self._global_middleware.send_command(command_name, data)] = (callback_handler, error_handler)

    def send_command_answear(self, result, data, request_id):
        self._global_middleware.send_command_answear("", result, data, request_id)
    
    def run_middleware_update(self):
        while(not self._transfer_queue.empty()):
            new_info = self._transfer_queue.get()
            if new_info["isCommand"]:
                if new_info["requestId"] in self._request_queue and new_info["name"] == "":
                    callbacks = self._request_queue[new_info["requestId"]]
                    if new_info["result"]:
                        if callbacks[0]:
                            callbacks[0](new_info)
                    else:
                        if callbacks[1]:
                            callbacks[1](new_info)
                    del self._request_queue[new_info["requestId"]]
                else:
                    self.command_update(new_info)
            else:
                self._status_update(new_info)

    def command_update(self, new_command):
        command_name = new_command["name"]
        if command_name in self._commands_available:
            self._commands_available[command_name](new_command)

    def check_if_subscribed(self, sub_status_name: str, status_name: str):
        sub_info = sub_status_name.split('/')
        status_info = status_name.split('/')

        bGatewayMatch = (sub_info[0] == '*') or (sub_info[0] == status_info[0])
        bTopicMatch = (sub_info[1] == '*') or (sub_info[1] == status_info[1])
        return bGatewayMatch and bTopicMatch
    
    def send_status(self, topic: str, new_status):
        self._global_middleware.send_status(topic, new_status)

    def _status_update(self, new_status):
        status_name = new_status["name"]
        data = new_status["data"]

        data_converted = self._data_converter.convert_data(status_name.split('/')[1], data)
        for sub_status_name, subscriber in self._subscribers.items():
            if self.check_if_subscribed(sub_status_name, status_name):
                subscriber.send_status(status_name, data_converted)
        