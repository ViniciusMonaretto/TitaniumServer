from threading import Thread
from time import sleep
from .server.server_handler import ServerHandler
from .visualization.visualization_manager import Visualization, VisualizationWebSocketHandler

import tornado.web

class AppManager:
    def __init__(self, middleware):
        self.m_Server = AppServer(middleware)
        self.thread = Thread(target = self.threaded_function, args = (10, ))
        self._middleware = middleware

    def threaded_function(self, args):
        self.m_Server.run()
    
    def run(self):
        self.thread.start()

    def join(self):
        self.thread.join()

class AppServer:
    def __init__(self, middleware):
        self._middleware = middleware
        self.app = self.make_app()       

    def run(self):
        self.value = 10
        self.app.listen(8888)  # Listen on port 8888
        print("Server is running on http://localhost:8888")
        #tornado.ioloop.PeriodicCallback(self.send_test_messages, 2000).start()
        tornado.ioloop.IOLoop.current().start()

    def make_app(self):
        return tornado.web.Application([
            (r"/", Visualization),
            (r"/websocket", VisualizationWebSocketHandler, {'middleware': self._middleware}),
            (r"/test", ServerHandler),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": "C:/Titanium/TitaniumServer/web/titanium-server/dist/titanium-server"})
        ],
        static_path="C:/Titanium/TitaniumServer/web/titanium-server/dist/titanium-server")
    