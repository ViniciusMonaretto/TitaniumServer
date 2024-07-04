import tornado.ioloop
import tornado.web
import tornado.websocket

class Visualization(tornado.web.RequestHandler):
    def get(self):
        self.render("../../web/titanium-server/dist/titanium-server/index.html")

class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")