from .data_converter.data_converter import DataConverter
from .subscriber_interface import SubscriberInterface
import threading

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

        if(not (id in self._status_subscriber)):
            print("Middleware::add_subscribe_from_status-> Error, subscriber {self._id} non subscribing {status_name}")
            return

        del self._status_subscriber[id]
        self._lock.release()

    def send_status(self, status_name, data):
        self._lock.acquire()
        for subscriber in self._subscriber_map:
            subscriber.on_status(status_name, data)

        self._lock.release()

class Middleware:
    def __init__(self):
        self._data_converter = DataConverter()
        self._subscribers = {}

    def add_subscribe_to_status(self, subscriber: SubscriberInterface, status_name):
        if(not (status_name in self._subscribers)):
            self._subscribers[status_name] = SubscriberManager(subscriber)

        self._subscribers[status_name].add_subscriber(subscriber)

    def remove_subscribe_from_status(self, subscriber, status_name):
        id = subscriber.get_id()
        if(not (id in self._subscribers)):
            print("Middleware::add_subscribe_from_status-> Error, subscriber {id} non existant")
            return
        
        self._subscribers[id].remove_subscriber(status_name)

    def send_status(self, status_name, data):
        data_converted = self._data_converter.convert_data(status_name, data)
        for subscriber in self._subscribers.values():
            subscriber.send_status(status_name, data_converted)
        