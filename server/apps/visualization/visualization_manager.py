import json
import tornado.web
import tornado.websocket

from dataModules.alarm import Alarm
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from services.config_storage.config_storage_commands import ConfigStorageCommand
from services.alarm_manager.alarm_manager_commands import AlarmManagerCommands
from support.logger import Logger 

from dataModules.panel import Panel
from middleware.subscriber_interface import SubscriberInterface
from middleware.status_subscriber import StatuSubscribers
from middleware.client_middleware import ClientMiddleware
from services.sensor_data_storage.sensor_data_storage_commands import SensorDataStorageCommands

from services.config_handler.config_handler_command import ConfigHandlerCommands

class Visualization(tornado.web.RequestHandler):
    def get(self):
        self.render("../../webApp/browser/index.html")

    def data_received(self, chunk: bytes):
        raise NotImplementedError()

class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    _id: str = ""
    _middleware:ClientMiddleware
    _is_init = False

    _id_to_topic_map: dict[str, str] = {}
    _status_subscribers: dict[str, SubscriberInterface] = {}
    _logger: Logger

    _event_subscriber: SubscriberInterface = None
    _calibrate_subscriber: SubscriberInterface = None

    def check_origin(self, origin):
        return True
    
    def data_received(self, chunk: bytes):
        raise NotImplementedError()
    
    def initialize_event_sub(self):
        self._event_subscriber = StatuSubscribers(self.send_event, "alarm-newevent-*" )
        self._middleware.add_subscribe_to_status( self._event_subscriber, "alarm-newevent-*")

    def initialize_ui_update_sub(self):
        self._calibrate_subscriber = StatuSubscribers(lambda data: self.send_ui_message(data["data"]), "ui-update-*" )
        self._middleware.add_subscribe_to_status( self._calibrate_subscriber, "ui-update-*")

    def initialize(self, middleware):
        self._logger = Logger()
        self._middleware  = middleware
        self._status_subscribers = {}
        self.initialize_event_sub()
        self.initialize_ui_update_sub()

################# Websocket functions #############################  
    def open(self, *args, **kwargs):
        self._logger.debug("WebSocket opened")
        self._is_init = True
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {}, 
                                      lambda data: self.add_subscribers(data["data"]),
                                      self.send_error_message)
        self.request_alarms({})

    def on_message(self, message):
        self._logger.debug("You said: " + message)
        message_obj = json.loads(message)
        payload = message_obj["payload"]
        try:
            if("addPanel" in message_obj["commandName"]):
                self.add_panel_request(payload)
            elif "removePanel" in message_obj["commandName"]:
                self.remove_panel(payload)
            elif "getStatusHistory" in message_obj["commandName"]:
                self.request_status(payload)
            elif "requestEvents" in message_obj["commandName"]:
                self.request_events(payload)
            elif "addAlarm" in message_obj["commandName"]:
                self.add_alarm(payload)
            elif "removeAlarm" in message_obj["commandName"]:
                self.remove_alarm(payload)
            elif "removeAllEvents" in message_obj["commandName"]:
                self.remove_all_events()
            elif "calibrate" in message_obj["commandName"]:
                self.calibrate_sensor(payload)
            else:
                self._logger.error("VisualizationWebSocketHandler:: unknown command: " + message_obj["commandName"])
        except Exception as e:
            self._logger.error(f"Exception occured on panel message: {e}")
    
    def on_close(self):
        self._logger.debug("WebSocket closed")
        self._middleware.remove_subscribe_from_status(self._event_subscriber, self._event_subscriber.get_topic())
        self._middleware.remove_subscribe_from_status(self._calibrate_subscriber, self._calibrate_subscriber.get_topic())
        self._calibrate_subscriber = None
        self._event_subscriber = None
        for subscriber_topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(self._status_subscribers[subscriber_topic], subscriber_topic)

    def send_error_message(self, message: str):
        self.send_message_to_ui("error", message)

    def safe_write_message(self, obj):
        try:
            self.write_message(obj)
        except Exception as e:
            self._logger.error(f"Failed to write message to UI: {e}")

    def send_message_to_ui(self, status, message):
        if(not self._is_init):
            return 
        obj = {
            "status": status,
            "message": message
        }
        tornado.ioloop.IOLoop.current().add_callback(self.safe_write_message, obj)

################# Status commands #############################
    def request_status(self, request):
        self._logger.info("Visualization.request_status: Incoming graph request")
        data = {
                'sensorInfos': request['sensorInfos'], 
                'websocketId': request['requestId']
            }
        if("beginDate" in request):
            data['beginDate'] = request["beginDate"]
        if("endDate" in request):
            data['endDate'] = request["endDate"]
    
        self._middleware.send_command(SensorDataStorageCommands.READ_SENSOR_INFO, data, self.send_status_history)                                    

    def send_status_history(self, data):
        self._logger.info("Visualization.send_status_history: graph send")
        self.send_message_to_ui("statusInfo", data)  

################# Panel commands #############################
    def add_panel_request(self, panel_info):
        self._middleware.send_command(ConfigHandlerCommands.ADD_PANEL, panel_info, 
                                      lambda data: (self.add_panel_subscriber_command(data["data"]), self.send_panel_info()),
                                      self.send_error_message)
        
    def remove_panel(self, panel_id):
        self._middleware.send_command(ConfigHandlerCommands.REMOVE_PANEL, {"id": panel_id}, 
                                      lambda data: self.remove_panel_subscriber(panel_id),
                                      self.send_error_message)
    
    def remove_panel_subscriber(self, panel_id):
        panel_topic = self._id_to_topic_map[panel_id]

        status_subscriber = self._status_subscribers[panel_topic]

        status_subscriber.remove_count()

        if not status_subscriber.has_subscribers():
            self._middleware.remove_subscribe_from_status( status_subscriber, panel_topic)
            del self._status_subscribers[panel_topic]

        del self._id_to_topic_map[panel_id]

        self.send_panel_info()

    def calibrate_sensor(self, callibrate_command):
        self._middleware.send_command(ConfigHandlerCommands.UPDATE_PANEL_FUNCTIONALITIES, callibrate_command)
    
    def send_panel_info(self):
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {}, 
                                      lambda data: self.send_ui_message(data["data"]),
                                      self.send_error_message)
        
    def send_ui_message(self, panels):
        self.send_message_to_ui("uiConfig", panels)
    
    def send_status(self, status_data):
        self.send_message_to_ui("sensorUpdate", status_data)
    
################# Alarms commands #############################
    def add_alarm(self, alarm_info):
        self._middleware.send_command(AlarmManagerCommands.ADD_ALARM, alarm_info, 
                                      self.send_alarm_added,
                                      self.send_error_message)
    
    def request_events(self, commands):
        self._middleware.send_command(ConfigStorageCommand.GET_EVENTS_LIST, commands, 
                                      self.send_events,
                                      self.send_error_message)

    def request_alarms(self, alarm_filter):
        self._middleware.send_command(AlarmManagerCommands.GET_ALARMS, alarm_filter, 
                                      self.send_alarm_info,
                                      self.send_error_message)
        
    def send_events(self, data: list[Alarm]):
        self.send_message_to_ui("eventListResponse", data) 
    
    def send_alarm_info(self, data: list[Alarm]):
        self.send_message_to_ui("alarmInfo", data) 
        
    def remove_alarm(self, alarm_id):
        self._middleware.send_command(AlarmManagerCommands.REMOVE_ALARM, {"id": alarm_id}, 
                                      self.send_alarm_removed,
                                      self.send_error_message)
     
    def send_alarm_added(self, data: Alarm):
        self._logger.info("Visualization.send_alarm_added: alarm added")
        self.send_message_to_ui("alarmAdded", data)  

    def send_alarm_removed(self, data):
        self._logger.info("Visualization.send_alarm_removed: alarm removed")
        self.send_message_to_ui("alarmRemoved", data)  
    
    def send_event(self, event_data):
        self.send_message_to_ui("eventInfoUpdate", event_data["data"])

    def remove_all_events(self):
         self._middleware.send_command(AlarmManagerCommands.REMOVE_ALL_EVENTS, {}, 
                                      lambda data: self.send_events(data),
                                      self.send_error_message)

################# Subscriber Functions #############################
    def add_subscribers(self, panels_info: dict[str, list[any]]):
        for panels in panels_info.values():
            for panel in panels:
                self.add_panel_subscriber(Panel(panel))
        
        self.send_panel_info()

    def add_panel_subscriber_command(self, panel: Panel):
        self.add_panel_subscriber(panel)
        self.send_panel_info()

    def add_panel_subscriber(self, panel: Panel):
        panel_topic = ClientMiddleware.get_status_topic(panel.gateway, panel.topic, panel.indicator)

        self._id_to_topic_map[panel.id] = panel_topic

        if(panel_topic not in self._status_subscribers):
            self._status_subscribers[panel_topic] = StatuSubscribers(self.send_status, panel_topic )
            self._middleware.add_subscribe_to_status(self._status_subscribers[panel_topic], panel_topic)
        self._status_subscribers[panel_topic].add_count()
        
