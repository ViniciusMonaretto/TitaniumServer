import json
import multiprocessing
import threading
import time
import tornado.web
import tornado.websocket

from dataModules.alarm import Alarm
from dataModules.gateway import GatewayStatus
from services.gateway_manager.gateway_manager_commands import GatewayManagerCommands
from services.report_generator.report_generator_commands import ReportGeneratorCommands
from services.config_storage.config_storage_commands import ConfigStorageCommand
from services.alarm_manager.alarm_manager_commands import AlarmManagerCommands
from support.logger import Logger

from dataModules.panel import Panel
from middleware.subscriber_interface import SubscriberInterface
from middleware.status_subscriber import StatuSubscribers
from middleware.client_middleware import ClientMiddleware
from services.sensor_data_storage.sensor_data_storage_commands import SensorDataStorageCommands

from services.config_handler.config_handler_command import ConfigHandlerCommands

import os
import base64
import mimetypes
import copy
import gc


class Visualization(tornado.web.RequestHandler):
    def get(self, path=None):
        # Serve the main Angular app for all routes
        self.render("../../webApp/browser/index.html")

    def data_received(self, chunk: bytes):
        raise NotImplementedError()


class VisualizationWebSocketHandler(tornado.websocket.WebSocketHandler):
    _id: str = ""
    _middleware: ClientMiddleware
    _is_init = False

    _id_to_topic_map: dict[str, str] = {}
    _status_subscribers: dict[str, SubscriberInterface] = {}
    _logger: Logger

    _alarm_event_subscriber: SubscriberInterface = None
    _gateway_status_subscriber: SubscriberInterface = None
    _calibrate_subscriber: SubscriberInterface = None

    def check_origin(self, origin):
        return True

    def data_received(self, chunk: bytes):
        raise NotImplementedError()

    def initialize_error_sub(self):
        self._error_subscriber = StatuSubscribers(
            lambda data: self.send_error_message(data["data"].message), "main-ui-error")
        self._middleware.add_subscribe_to_status(
            self._error_subscriber, "main-ui-error")

    def initialize_event_sub(self):
        self._alarm_event_subscriber = StatuSubscribers(
            self.send_event, "alarm-newevent-*")
        self._middleware.add_subscribe_to_status(
            self._alarm_event_subscriber, "alarm-newevent-*")

    def initialize_ui_update_sub(self):
        self._calibrate_subscriber = StatuSubscribers(
            lambda data: self.send_ui_message(data["data"]), "ui-update-*")
        self._middleware.add_subscribe_to_status(
            self._calibrate_subscriber, "ui-update-*")

        self._gateway_status_subscriber = StatuSubscribers(
            self.send_gateway_status, "gateway-statusupdate-*")
        self._middleware.add_subscribe_to_status(
            self._gateway_status_subscriber, "gateway-statusupdate-*")

    def initialize(self, middleware):
        self._logger = Logger()
        self._middleware = middleware
        self._status_subscribers = {}
        self.initialize_event_sub()
        self.initialize_ui_update_sub()
        self.initialize_error_sub()


################# Websocket functions #############################

    def open(self, *args, **kwargs):
        self._logger.debug("WebSocket opened")
        self._is_init = True
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {},
                                      lambda data: self.add_subscribers(
                                          data["data"]),
                                      self.send_error_message)
        self.request_alarms({})

    def on_message(self, message):
        self._logger.debug("You said: " + message)
        message_obj = json.loads(message)
        payload = message_obj["payload"]
        try:
            if ("addPanel" in message_obj["commandName"]):
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
            elif "updatePanelInfo" in message_obj["commandName"]:
                self.update_panel_info(payload)
            elif "addGroupPanel" in message_obj["commandName"]:
                self.add_panel_group(payload)
            elif "removeGroupPanel" in message_obj["commandName"]:
                self.remove_panel_group(payload)
            elif "updateGroupPanel" in message_obj["commandName"]:
                self.update_panel_group(payload)
            elif "generaterReport" in message_obj["commandName"]:
                self.generate_report(payload)
            elif "updateGateways" in message_obj["commandName"]:
                self.update_gateways(payload)
            elif "getGateways" in message_obj["commandName"]:
                self.get_gateways(payload)
            else:
                self._logger.error(
                    "VisualizationWebSocketHandler:: unknown command: " + message_obj["commandName"])
        except Exception as e:
            self._logger.error(f"Exception occured on websocket message: {e}")

    def on_close(self):
        self._logger.debug("WebSocket closed")
        self._middleware.remove_subscribe_from_status(
            self._alarm_event_subscriber, self._alarm_event_subscriber.get_topic())
        self._middleware.remove_subscribe_from_status(
            self._calibrate_subscriber, self._calibrate_subscriber.get_topic())
        self._middleware.remove_subscribe_from_status(
            self._gateway_status_subscriber, self._gateway_status_subscriber.get_topic())
        self._middleware.remove_subscribe_from_status(
            self._error_subscriber, self._error_subscriber.get_topic())

        self._calibrate_subscriber = None
        self._alarm_event_subscriber = None
        self._gateway_status_subscriber = None
        self._error_subscriber = None

        for subscriber_topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(
                self._status_subscribers[subscriber_topic], subscriber_topic)

    def send_error_message(self, message: str):
        self.send_message_to_ui("error", message)

    def safe_write_message(self, obj):
        try:
            if not self.ws_connection or self.ws_connection.is_closing():
                return
            self.write_message(obj)
        except tornado.websocket.WebSocketClosedError:
            # Client disconnected, this is normal
            pass
        except Exception as e:
            self._logger.error(f"Failed to write message to UI: {e}")
        finally:
            # Libera memória após envio
            should_clear = isinstance(
                obj, dict) and "message" in obj and "isCommand" in obj["message"] and obj["message"]["isCommand"] == True
            try:
                if should_clear:
                    message = obj["message"]
                    if isinstance(message, dict):
                        if "info" in message:
                            message["info"].clear()  # Limpa dados grandes
                        message.clear()  # Limpa mensagem
                    elif hasattr(message, 'clear'):
                        message.clear()
                    obj.clear()  # Limpa objeto
            except Exception as cleanup_error:
                self._logger.warning(
                    f"Erro durante limpeza de memória: {cleanup_error}")
            finally:
                gc.collect()  # Força garbage collection

    def send_message_to_ui(self, status, message):
        if (not self._is_init):
            return

        # Copia os dados para evitar problemas de referência
        message_copy = copy.deepcopy(message)

        obj = {
            "status": status,
            "message": message_copy
        }
        tornado.ioloop.IOLoop.current().add_callback(self.safe_write_message, obj)

        # Limpa os dados originais após criar a cópia
        if isinstance(message, dict) and "isCommand" in message and message["isCommand"] == True:
            message.clear()

################# Status commands #############################
    def request_status(self, request):
        self._logger.info(
            "Visualization.request_status: Incoming graph request")
        data = {
            'sensorInfos': request['sensorInfos'],
            'websocketId': request['requestId']
        }
        if ("beginDate" in request):
            data['beginDate'] = request["beginDate"]
        if ("endDate" in request):
            data['endDate'] = request["endDate"]

        self._middleware.send_command(
            SensorDataStorageCommands.READ_SENSOR_INFO,
            data,
            self.send_status_history,
            self.send_error_message)

    def send_status_history(self, data):
        self._logger.info("Visualization.send_status_history: graph send")

        # Log do tamanho dos dados para monitoramento
        if 'info' in data:
            total_points = sum(len(sensor_data)
                               for sensor_data in data['info'].values())
            self._logger.debug(
                f"Enviando {total_points} pontos de dados para {len(data['info'])} sensores")

        # Envia os dados (a cópia e limpeza são feitas em send_message_to_ui)
        self.send_message_to_ui("statusInfo", data)


################# Panel commands #############################


    def add_panel_request(self, panel_info):
        self._middleware.send_command(ConfigHandlerCommands.ADD_PANEL, panel_info,
                                      lambda data: (self.add_panel_subscriber_command(
                                          data["data"]), self.send_panel_info()),
                                      self.send_error_message)

    def remove_panel(self, panel_id):
        self._middleware.send_command(ConfigHandlerCommands.REMOVE_PANEL, {"id": panel_id},
                                      lambda data: self.remove_panel_subscriber(
                                          panel_id),
                                      self.send_error_message)

    def remove_panel_subscriber(self, panel_id):
        panel_topic = self._id_to_topic_map[panel_id]

        status_subscriber = self._status_subscribers[panel_topic]

        if status_subscriber == None:
            return

        status_subscriber.remove_count()

        if not status_subscriber.has_subscribers():
            self._middleware.remove_subscribe_from_status(
                status_subscriber, panel_topic)
            del self._status_subscribers[panel_topic]

        del self._id_to_topic_map[panel_id]

        self.send_panel_info()

    def update_panel_info(self, update_panel_command):
        self._middleware.send_command(
            ConfigHandlerCommands.UPDATE_PANEL_FUNCTIONALITIES, update_panel_command)

################# Panel Group commands #############################
    def add_panel_group(self, group_info):
        self._middleware.send_command(ConfigHandlerCommands.ADD_PANEL_GROUP, group_info,
                                      lambda data: self.send_panel_info(),
                                      self.send_error_message)

    def remove_panel_group(self, group_info):
        self._middleware.send_command(ConfigHandlerCommands.REMOVE_PANEL_GROUP, group_info,
                                      lambda data: self.send_panel_info(),
                                      self.send_error_message)

    def update_panel_group(self, group_info):
        self._middleware.send_command(ConfigHandlerCommands.UPDATE_PANEL_GROUP, group_info,
                                      lambda data: self.send_panel_info(),
                                      self.send_error_message)

    def send_panel_info(self):
        self._middleware.send_command(ConfigHandlerCommands.GET_PANEL_LIST, {},
                                      lambda data: self.send_ui_message(
                                          data["data"]),
                                      self.send_error_message)

    def send_ui_message(self, panels):
        self.send_message_to_ui("uiConfig", panels)

    def send_status(self, status_data):
        self.send_message_to_ui("sensorUpdate", status_data["data"].to_dict())

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

################# Report commands #############################
    def generate_report(self, request):
        data = {
            'sensorInfos': request['sensorInfos'],
            'websocketId': request['requestId']
        }
        if ("beginDate" in request):
            data['beginDate'] = request["beginDate"]
        if ("endDate" in request):
            data['endDate'] = request["endDate"]
        self._middleware.send_command(ReportGeneratorCommands.GENERATE_REPORT, data,
                                      self.send_report,
                                      self.send_error_message)

    def send_report(self, data):
        file_path = data["data"]["file_path"]
        if not os.path.isfile(file_path):
            self.send_error_message(f"File not found: {file_path}")
            return

        with open(file_path, "rb") as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            filename = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            message = {
                "filename": filename,
                "filedata": encoded,
                "mimetype": mime_type
            }
            self.send_message_to_ui("report", message)

################# Subscriber Functions #############################
    def add_subscribers(self, info: {'CalibrateUpdate': bool, 'PanelsInfo': dict[str, dict]}):
        panels_info = info['PanelsInfo']
        for group_id in panels_info.keys():
            group_data = panels_info[group_id]
            if "panels" in group_data:
                for panel in group_data["panels"]:
                    self.add_panel_subscriber(Panel(panel))

        self.send_panel_info()

    def add_panel_subscriber_command(self, panel: Panel):
        self.add_panel_subscriber(panel)
        self.send_panel_info()

    def add_panel_subscriber(self, panel: Panel):
        panel_topic = ClientMiddleware.get_gateway_status_topic(panel.gateway)

        self._id_to_topic_map[panel.id] = panel.gateway

        if (panel_topic not in self._status_subscribers):
            self._status_subscribers[panel_topic] = StatuSubscribers(
                self.send_status, panel_topic)
            self._middleware.add_subscribe_to_status(
                self._status_subscribers[panel_topic], panel_topic)
        self._status_subscribers[panel_topic].add_count()


################# Gateway status commands #############################

    def send_gateway_status(self, gateway_status: list[GatewayStatus]):
        self.send_message_to_ui("gatewayStatus", gateway_status)

    def update_gateways(self, payload):
        self._middleware.send_command(GatewayManagerCommands.REQUEST_UPDATE_GATEWAYS, payload,
                                      None,
                                      self.send_error_message)

    def get_gateways(self, payload):
        self._middleware.send_command(GatewayManagerCommands.GET_GATEWAYS, payload,
                                      None,
                                      self.send_error_message)
