import tornado.ioloop
import tornado.web
import tornado.websocket
import json

from .server_data import ServerDataInput

class TitaniumServer:
    def __init__(self, middleware):
        self._middleware = middleware
        self.app = self.make_app()

    def run(self):
        self.app.listen(3000)  # Listen on port 3000
        print("Receiver Server is running on http://localhost:3000")
        tornado.ioloop.IOLoop.current().start()

    def make_app(self):
        return tornado.web.Application([
            (r"/info", InfoReceiverHandler, {"middleware": self._middleware})
        ])
    
class InfoReceiverHandler(tornado.web.RequestHandler):
    def initialize(self, middleware):
        self._middleware = middleware
    
    def get(self):
        self.write("Hello, world")

    def post(self):
        try:
            data = ServerDataInput(json.loads(self.request.body))
            # You can process the received data here
            print("received data from sensor {}: {}", data.id, data.value)
            self.set_status(200)
            self.write({"status": "success"})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "Invalid JSON"})