import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json

from apps.visualization.panel import Panel

class Visualization(tornado.web.RequestHandler):
    def get(self):
        self.render("../../web/titanium-server/dist/titanium-server/src/index.html")

class StatuSubscribers:
    def __init__(self, send_message_callback, status_name):
        self._callback = send_message_callback
        self._status = status_name
        self._count = 0

    def send_message(self, data):
        self._callback("{ 'name': {self._status}, 'data': {data} }") 

    def add_count(self):
        self._count+=1

    def remove_count(self):
        self._count-=1

class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, middleware):
        self._middleware = middleware
        self._status_subscribers = {}

        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "ui_config.json")

        with open(json_directory, 'r') as json_file:
            try:
                data = json.load(json_file)  # Load the JSON data
                # Process the JSON data (replace this with your logic)
                self._ui_config = self.add_panels(data)

                print(f"Processing file: {json_directory}")
            except json.JSONDecodeError as e:
                print(f"Error processing file {json_directory}: {e}")
    
    def open(self):
        print("WebSocket opened")
        self.write_message("{ 'uiConfig': {self._ui_config} }")

    def on_message(self, message):
        self.write_message("You said: " + message)
        if("addPanel" in message):
            panel_info = json.load(message["panelInfo"])
            

    def add_panels(self, panels_info):
        for panel_info in panels_info:
            self.add_panel(panel_info)
    
    def add_panel(self, panel_info):
        panel = Panel(panel_info)
        self._middleware.add_subscribe_to_status(panel._status)

        if(panel._status in self._status_subscribers):
            self._status_subscribers[panel._status] = StatuSubscribers(self.send_status, panel._status)
            self._middleware.add_subscribe_to_status(self._status_subscribers[panel._status], panel._status)
        self._status_subscribers[panel._status].add_count()
    
    def send_status(self, status_data):
        obj = "{ 'status': {status_data} }"
        self.write_message(obj)


    def on_close(self):
        print("WebSocket closed")