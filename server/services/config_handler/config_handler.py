import json
import os
import threading
from typing import Union
from middleware.client_middleware import ClientMiddleware

from dataModules.panel import Panel
from middleware.status_subscriber import StatuSubscribers
from services.sensor_data_storage.sensor_data_storage import SensorDataStorage
from support.logger import Logger


from .config_handler_command import ConfigHandlerCommands
from ..service_interface import ServiceInterface

from ..config_storage.config_storage import ConfigStorage

DB_CONFIG = "db_status_saves.json"
DB_NAME = "titanium_server_db.db"

class ConfigHandler(ServiceInterface):
    _panels_info: dict[str: list[Panel]] = {}
    _status_subscribers = {}

    def __init__(self, middleware: ClientMiddleware, config_storage: ConfigStorage, sensor_data_storage: SensorDataStorage):
        self._logger = Logger()
        self._middleware = middleware
        self._config_storage = config_storage
        self._sensor_data_storage = sensor_data_storage

        self.initialize_commands()
        self.initialize_system()

        self._logger.info("ConfigHandler initialized")

    def initialize_commands(self):
        commands = {
            ConfigHandlerCommands.ADD_PANEL: self.add_panel_command,
            ConfigHandlerCommands.REMOVE_PANEL: self.remove_panel_command,
            ConfigHandlerCommands.GET_PANEL_LIST: self.get_panels_list_command
            }
        self._middleware.add_commands(commands)
    
    def read_default_config(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "..", "..", "config",  "ui_config.json")
        with open(json_directory, 'r', encoding='utf-8') as json_file:
            try:
                data = json.load(json_file)  # Load the JSON data
                # Process the JSON data (replace this with your logic)
                self.add_panels(data)

                self._logger.info(f"Processing file: {json_directory}")
            except json.JSONDecodeError as e:
                self._logger.error(f"VisualizationWebSocketHandler:: Error processing file {json_directory}: {e}")
    
    def initialize_panels_from_db(self, panels_infos):
        for panel_info in panels_infos:
            self.add_panel(panel_info)

    def initialize_system(self):
        panels_infos = self._config_storage.get_panels()
        if len(panels_infos) == 0:
            self.read_default_config()
        else:
            self.initialize_panels_from_db(panels_infos)

    def calibration_update_received(self, status_info, panel: Panel):
        data = status_info["data"]

        panel.offset = data["offset"]
        panel.gain = data["gain"]
        self._config_storage.update_panel(panel)
        self.send_ui_update_action()

    def subscribe_to_status(self, gateway, status_name, indicator, panel):
        topic = ClientMiddleware.get_status_topic(gateway, status_name, indicator)
        if(not topic in self._status_subscribers):
            self._status_subscribers[topic] = StatuSubscribers(lambda status_info : self.calibration_update_received(status_info, panel), topic)
            self._middleware.add_subscribe_to_status(self._status_subscribers[topic], topic)


    def add_group(self, group_name) -> Union[bool, str]:
        if group_name in self._panels_info:
            return (False, "Group name already added")
        self._panels_info[group_name] = []
        return (True, "Sucess")

    def add_panels(self, panels_info):
        for group_name in panels_info.keys():
            if group_name not in self._panels_info:
                self._panels_info[group_name] = []
            for panel_info in panels_info[group_name]:
                self.add_panel(panel_info)

    def add_panel(self, panel_info) -> Union[bool, str]:
        result = False
        message = ""
        panel = Panel(panel_info)

        group_name = panel.group

        if group_name not in self._panels_info:
            self.add_group(group_name)
        
        index = -1
        if(not panel.id):
            index = self._config_storage.add_panel(panel)
        else:
            index = panel.id
        if( index != -1):
            panel.id = index
            result, message = self._sensor_data_storage.add_new_subscription(panel.topic, panel.gateway, panel.indicator)
        
            if result:
                self._panels_info[group_name].append(panel)

        return result, message
    
    def add_panel_command(self, command):
        data = command["data"]

        result, message = self.add_panel(data)

        if result:
            self._middleware.send_command_answear( result, self._panels_info[data["group"]][-1], command["requestId"])
        else:
            self._middleware.send_command_answear( result, message, command["requestId"])
        
    
    def remove_panel(self, panel_id) -> Union[bool, str]:
        try: 
            for panels in self._panels_info.values():
                for idx, panel in enumerate(panels):
                    if panel.id == panel_id:
                        wait_flag = threading.Event()
                        self._sensor_data_storage.erase_sensor_info([panel.get_full_name()], 
                                                                    None,
                                                                    None,
                                                                    lambda a,b : wait_flag.set())
                        wait_flag.wait(180)

                        result = self._config_storage.remove_panel(panel_id)

                        if (result):   
                            del panels[idx]
                            return True, "Painél Removido"
        except Exception as e:
            self._logger.error(f"ConfigHandler::remove_panel: Error while removing panel {e}")
        
        return False, "Remove panel error: Panel not found"
    
    def remove_panel_command(self, command):
        data = command["data"]

        result, message = self.remove_panel(data["id"])

        if result:
            self._middleware.send_command_answear( result, {}, command["requestId"])
        else:
            self._middleware.send_command_answear( result, message, command["requestId"])

    def create_object_from_panels_info(self):
        obj = {}

        for group in self._panels_info.keys():
            obj[group] = [panel.to_json() for panel in self._panels_info[group] ]

        return obj
    
    def get_panels_list_command(self, command):
        self._middleware.send_command_answear( True, self.create_object_from_panels_info(), command["requestId"])

    def send_ui_update_action(self):
        self._middleware.send_status("ui-update-*", self.create_object_from_panels_info()) 
