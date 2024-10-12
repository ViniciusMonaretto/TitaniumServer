from .data_converter.data_converter import DataConverter
import threading

class SubscriberManager:
    def __init__(self, subscriber_obj):
        if(subscriber_obj.get_id() == -1):
            raise Exception("Subscriver Id is invalid")
        self._status_subscriber = {}
        self._subscriber_obj = subscriber_obj
        self._lock = threading.Lock()
        self._id = subscriber_obj.get_id()
    
    def add_subscriber(self, status_name):
        self._lock.acquire()

        self._status_subscriber[status_name] = True
        
        self._lock.release()

    def remove_subscriber(self, status_name):
        self._lock.acquire()

        if(not (status_name in self._status_subscriber)):
            print("Middleware::add_subscribe_from_status-> Error, subscriber {self._id} non subscribing {status_name}")
            return

        del self._status_subscriber[status_name]
        self._lock.release()

    def send_status(self, status_name, data):
        self._lock.acquire()
        if(status_name in self._status_subscriber):
            self._subscriber_obj.on_status(status_name, data)

        self._lock.release()

class Middleware:
    def __init__(self):
        self._data_converter = DataConverter()
        self._subscribers = {}

    def add_subscribe_to_status(self, subscriber, status_name):
        id = subscriber.get_id()
        if(not (subscriber in self._subscribers)):
            self._subscribers[id] = SubscriberManager(subscriber)

        self._subscribers[id].add_subscriber(status_name)

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
        