import uuid
from .subscriber_interface import SubscriberInterface


class StatuSubscribers(SubscriberInterface):
    def __init__(self, send_message_callback, status_name):
        self._callback = send_message_callback
        self._status = status_name
        self._count = 0
        self._id = str(uuid.uuid1())

    def on_status(self, status_name, data, sub_status_name):
        self._callback({ 'name': status_name, 'data': data, 'subStatusName': sub_status_name}) 

    def add_count(self):
        self._count+=1

    def has_subscribers(self):
        return self._count > 0

    def get_id(self):
        return self._id

    def remove_count(self):
        self._count-=1

    def get_topic(self):
        return self._status
