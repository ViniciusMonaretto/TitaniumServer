from middleware.subscriber_interface import SubscriberInterface


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
