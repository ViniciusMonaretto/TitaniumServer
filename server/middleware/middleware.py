from .data_converter.data_converter import DataConverter
from .subscriber_interface import SubscriberInterface
import threading
import multiprocessing

class SubscriberManager:
    _subscriber_map = {}

    def __init__(self, status_name):
        self._status_name = status_name
        self._lock = threading.Lock()
    
    def add_subscriber(self, subscriber: SubscriberInterface):
        self._lock.acquire()

        self._subscriber_map[subscriber.get_id()] = subscriber
        
        self._lock.release()

    def remove_subscriber(self, id):
        self._lock.acquire()

        if(not (id in self._subscriber_map)):
            print("Middleware::add_subscribe_from_status-> Error, subscriber {self._id} non subscribing {status_name}")
            return

        del self._subscriber_map[id]
        self._lock.release()

    def send_status(self, status_name, data):
        self._lock.acquire()
        for subscriber_id in self._subscriber_map:
            subscriber = self._subscriber_map[subscriber_id]
            subscriber.on_status(status_name, data)

        self._lock.release()

class ClientMiddleware:
    def __init__(self, middleware):
        self._data_converter = DataConverter()
        self._subscribers = {}
        self._transfer_queue:  multiprocessing.Queue = middleware.add_new_middleware_listener()

    def add_subscribe_to_status(self, subscriber: SubscriberInterface, status_name):
        if(not (status_name in self._subscribers)):
            self._subscribers[status_name] = SubscriberManager(subscriber)

        self._subscribers[status_name].add_subscriber(subscriber)

    def remove_subscribe_from_status(self, subscriber, status_name):
        id = subscriber.get_id()
        if(not (status_name in self._subscribers)):
            print("Middleware::add_subscribe_from_status-> Error, subscriber {id} non existant")
            return
        
        self._subscribers[status_name].remove_subscriber(id)

    def run_status_update(self):
        while(not self._transfer_queue.empty()):
            new_status = self._transfer_queue.get()
            status_name = new_status["statusName"]
            data = new_status["data"]

            data_converted = self._data_converter.convert_data(status_name, data)
            for sub_status_name, subscriber in self._subscribers.items():
                if sub_status_name == status_name:
                    subscriber.send_status(status_name, data_converted)

class Middleware:
    def __init__(self):
        self._subscriber_queues = []

    def add_new_middleware_listener(self):
        queue = multiprocessing.Queue()
        self._subscriber_queues.append(queue)
        return queue

    def send_status(self, status_name, data):
        for queue in self._subscriber_queues:
            queue.put({"statusName": status_name, "data": data})
        