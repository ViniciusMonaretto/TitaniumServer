import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import json
import uuid
from support.logger import Logger 

from services.config_handler.panel import Panel
from middleware.subscriber_interface import SubscriberInterface
from middleware.status_subscriber import StatuSubscribers
from middleware.middleware import ClientMiddleware
from services.status_saver.status_saver_commands import Commands as StatusSaverCommands

from services.config_handler.config_handler_command import ConfigHandlerCommands

class Visualization(tornado.web.RequestHandler):
    def get(self):
        self.render("../../webApp/index.html")

class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    _panels_count = 1
    _id_to_topic_map: dict[str, str] = {}
    _status_subscribers: dict[str, SubscriberInterface] = {}

    def check_origin(self, origin):
        return True

    def initialize(self, middleware):
        self._logger = Logger()
        self.id = str(uuid.uuid4())
        self._middleware:ClientMiddleware  = middleware
        self._status_subscribers = {}
    
    def open(self):
        self._logger.debug("WebSocket opened")
        self._is_init = True
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {}, 
                                      lambda data: self.add_subscribers(data["data"]),
                                      lambda message: self.send_error_message(message))
    
    def send_panel_info(self):
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {}, 
                                      lambda data: self.send_message_to_ui("uiConfig", data["data"]),
                                      lambda message: self.send_error_message(message))

    def on_message(self, message):
        self._logger.debug("You said: " + message)
        messageObj = json.loads(message)
        payload = messageObj["payload"]
        try:
            if("addPanel" in messageObj["commandName"]):
                self.add_panel_request(payload)
            elif "removePanel" in messageObj["commandName"]:
                self.remove_panel(payload)
            elif "getStatusHistory" in messageObj["commandName"]:
                self.request_status(payload)
            else:
                self._logger.error("VisualizationWebSocketHandler:: unknown command: " + messageObj["commandName"])
        except Exception as e:
            self._logger.error(f"Exception occured on panel message: {e}")

    def request_status(self, request):
        data = {'table':request["table"], 'gateway': request["gateway"], 'timestamp': request["timestamp"]}
        self._middleware.send_command(StatusSaverCommands.GET_TABLE_INFO, data, self.send_status_history)                                    
    
    def send_status_history(self, data):
        self.send_message_to_ui("statusInfo", data)  

    def add_panel_request(self, panel_info):
        self._middleware.send_command(ConfigHandlerCommands.ADD_PANEL, panel_info, 
                                      lambda data: (self.add_panel_subscriber_command(data["data"]), self.send_panel_info()),
                                      lambda message: self.send_error_message(message))
        
    def remove_panel(self, panel_id):
        self._middleware.send_command(ConfigHandlerCommands.REMOVE_PANEL, {"id": panel_id}, 
                                      lambda data: self.remove_panel_subscriber(panel_id),
                                      lambda message: self.send_error_message(message))
    
    def remove_panel_subscriber(self, panel_id):
        panel_topic = self._id_to_topic_map[panel_id]

        status_subscriber = self._status_subscribers[panel_topic]

        status_subscriber.remove_count()

        if not status_subscriber.has_subscribers():
            self._middleware.remove_subscribe_from_status( status_subscriber, panel_topic)
            del self._status_subscribers[panel_topic]

        del self._id_to_topic_map[panel_id]

        self.send_panel_info()
    
    def get_panel_topic(self, topic: Panel, gateway):
        return  gateway + "/" + topic
    
    def add_subscribers(self, panels: list[object]):
        for panel in panels:
            self.add_panel_subscriber(panel["topic"], panel["gateway"], panel["id"])
        
        self.send_panel_info()

    def add_panel_subscriber_command(self, panel: Panel):
        self.add_panel_subscriber(panel._topic, panel._gateway, panel._id)
        self.send_panel_info()

    def add_panel_subscriber(self, topic: str, gateway: str, id: int):
        panel_topic = self.get_panel_topic(topic, gateway)

        self._id_to_topic_map[id] = panel_topic

        if(panel_topic not in self._status_subscribers):
            self._status_subscribers[panel_topic] = StatuSubscribers(self.send_status, panel_topic, self.id + str(self._panels_count) )
            self._middleware.add_subscribe_to_status(self._status_subscribers[panel_topic], panel_topic)
        self._status_subscribers[panel_topic].add_count()
        self._panels_count+=1

        
    
        
    def send_error_message(self, message: str):
        self.send_message_to_ui("error", message)

    def send_message_to_ui(self, status, message):
        if(not self._is_init):
            return 
        obj = {
            "status": status,
            "message": message
        }
        self.write_message(obj)

    def send_status(self, status_data):
        self.send_message_to_ui("sensorUpdate", status_data)

    def on_close(self):
        self._logger.debug("WebSocket closed")
        for subscriber_topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(self._status_subscribers[subscriber_topic], subscriber_topic)