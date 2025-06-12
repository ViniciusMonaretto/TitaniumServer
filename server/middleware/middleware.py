import multiprocessing
import uuid
from support.logger import Logger

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
        