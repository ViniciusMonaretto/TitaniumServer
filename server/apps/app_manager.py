from threading import Thread
from time import sleep
from .visualization.visualization_manager import Visualization, VisualizationWebSocketHandler

from middleware.middleware import ClientMiddleware

import tornado.web
import os

class AppManager:
    def __init__(self, middleware):
        self._middleware = ClientMiddleware(middleware)
        self.m_Server = AppServer(self._middleware)
        self.thread = Thread(target = self.threaded_function, args = (10, ))   

    def threaded_function(self, args):
        self.m_Server.run()
    
    def run(self):
        self.thread.start()

    def join(self):
        self.thread.join()

class AppServer:
    def __init__(self, middleware: ClientMiddleware):
        self._middleware = middleware
        self.app = self.make_app()       

    def run(self):
        self.value = 10
        self.app.listen(8888)  # Listen on port 8888
        print("Server is running on http://localhost:8888")
        tornado.ioloop.PeriodicCallback(self.send_test_messages, 200).start()
        tornado.ioloop.IOLoop.current().start()

    def send_test_messages(self):
        self._middleware.run_middleware_update()

    def make_app(self):
        base_dir = os.path.dirname(__file__)  # Current directory of the server script
        angular_dist = os.path.join(base_dir, "../webApp")
        return tornado.web.Application([
            (r"/websocket", VisualizationWebSocketHandler, {'middleware': self._middleware}),
            (r"/(.*\.(js|css|ico|png|jpg|jpeg|woff|woff2|ttf|svg))", tornado.web.StaticFileHandler, {"path": angular_dist}),
            (r"/", Visualization),
            (r"/main", Visualization)
        ],
        static_path="C:/Titanium/TitaniumServer/web/titanium-server/dist/titanium-server")
    