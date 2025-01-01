import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import uuid

from threading import Thread
from threading import Lock

from apps.visualization.panel import Panel
from middleware.subscriber_interface import SubscriberInterface
from middleware.status_subscriber import StatuSubscribers

ui_visualizer_lock = Lock()

class Visualization(tornado.web.RequestHandler):
    def get(self):
        self.render("../../web/titanium-server/dist/titanium-server/src/index.html")

class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    _panels_count = 1

    def check_origin(self, origin):
        return True
    
    def initialize(self, middleware):
        self.id = str(uuid.uuid4())
        self._middleware = middleware
        self._status_subscribers: dict[str, SubscriberInterface] = {}

        ui_visualizer_lock.acquire()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "ui_config.json")

        with open(json_directory, 'r') as json_file:
            try:
                data = json.load(json_file)  # Load the JSON data
                # Process the JSON data (replace this with your logic)
                self.add_panels(data)
                self._ui_config = data

                print(f"Processing file: {json_directory}")
            except json.JSONDecodeError as e:
                print(f"Error processing file {json_directory}: {e}")
        ui_visualizer_lock.release()

    def periodic_status_sender(self):
        self._middleware.run_status_update()
    
    def open(self):
        print("WebSocket opened")
        self._is_init = True
        self.send_message_to_ui("uiConfig", self._ui_config)

    def on_message(self, message):
        print("You said: " + message)
        messageObj = json.loads(message)
        payload = messageObj["payload"]
        try:
            if("addPanel" in messageObj["commandName"]):
                self.add_new_panel(payload)
            elif "removePanel" in messageObj["commandName"]:
                self.remove_panel(payload)
            else:
                print("unknown command: " + messageObj["commandName"])
        except Exception as e:
            print(f"Exception occured on panel message: {e}")

    def add_new_panel(self, panel_info):
        new_panel_info = self.add_panel(panel_info)
        self._ui_config["panels"].append(new_panel_info)
        self.update_ui_file(self._ui_config)
        self.send_message_to_ui("uiConfig", self._ui_config)
    
    def remove_panel(self, panel_id):
        for index, panel in enumerate(self._ui_config["panels"]):
            if(panel['id'] == panel_id):
                del self._ui_config["panels"][index]
        self.update_ui_file(self._ui_config)
        self.send_message_to_ui("uiConfig", self._ui_config)

    def send_message_to_ui(self, status, message):
        if(not self._is_init):
            return 
        obj = {
            "status": status,
            "message": message
        }

        self.write_message(obj)
        

    def add_panels(self, panels_info):
        for panel_info in panels_info['panels']:
            self.add_panel(panel_info)

    def update_ui_file(self, panels_info):
        ui_visualizer_lock.acquire()
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "ui_config.json")

        with open(json_directory, 'w') as json_file:
            json_file.write( json.dumps(panels_info))
        ui_visualizer_lock.release()
    
    def get_panel_topic(self, panel: Panel):
        return str(panel._gateway) + "/" + panel._topic

    def add_panel(self, panel_info):
        panel = Panel(panel_info)

        panel_topic = self.get_panel_topic(panel)

        if(panel_topic not in self._status_subscribers):
            self._status_subscribers[panel_topic] = StatuSubscribers(self.send_status, panel_topic, self.id + str(self._panels_count) )
            self._middleware.add_subscribe_to_status(self._status_subscribers[panel_topic], panel_topic)
        self._status_subscribers[panel_topic].add_count()
        self._panels_count+=1

        panel_info["id"] = panel._id

        return panel_info
    
    def send_status(self, status_data):
        self.send_message_to_ui("sensorUpdate", status_data)

    def on_close(self):
        print("WebSocket closed")
        for subscriber_topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(self._status_subscribers[subscriber_topic], subscriber_topic)