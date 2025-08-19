import os
from threading import Thread
import tornado.web

from support.logger import Logger
from .visualization.visualization_manager import Visualization, VisualizationWebSocketHandler

from middleware.client_middleware import ClientMiddleware


class AppManager:
    def __init__(self, middleware):
        self._middleware = ClientMiddleware(middleware)
        self._server = AppServer(self._middleware)
        self._thread = Thread(target=self.threaded_function)

    def threaded_function(self):
        self._server.run()

    def run(self):
        self._thread.start()

    def join(self):
        self._thread.join()


class AppServer:
    _logger: Logger

    def __init__(self, middleware: ClientMiddleware):
        self._middleware = middleware
        self.app = self.make_app()
        self._logger = Logger()

    def run(self):
        self.app.listen(8888)  # Listen on port 8888
        self._logger.info("Server is running on http://localhost:8888")
        tornado.ioloop.PeriodicCallback(self.send_test_messages, 200).start()
        tornado.ioloop.IOLoop.current().start()

    def send_test_messages(self):
        self._middleware.run_middleware_update()

    def make_app(self):
        # Current directory of the server script
        base_dir = os.path.dirname(__file__)
        angular_dist = os.path.join(base_dir, "../webApp/browser")
        return tornado.web.Application([
            (r"/websocket", VisualizationWebSocketHandler,
             {'middleware': self._middleware}),
            (r"/(.*\.(js|css|ico|png|jpg|jpeg|woff|woff2|ttf|svg))",
             tornado.web.StaticFileHandler, {"path": angular_dist}),
            (r"/(.*)", Visualization),  # Catch all routes for SPA
        ],
            static_url_prefix="/")
