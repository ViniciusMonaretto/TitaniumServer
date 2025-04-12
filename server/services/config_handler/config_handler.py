import sqlite3
import json
import os
from datetime import datetime
from typing import Union
from middleware.status_subscriber import StatuSubscribers
from middleware.middleware import ClientMiddleware
import uuid

from .panel import Panel

from .config_handler_command import ConfigHandlerCommands

from support.logger import Logger
from ..service_interface import ServiceInterface

from ..status_saver.status_saver import StatusSaver

DB_CONFIG = "db_status_saves.json"
DB_NAME = "titanium_server_db.db"

class ConfigHandler(ServiceInterface):
    _panels_info: dict[str: list[Panel]] = {}
    def __init__(self, middleware: ClientMiddleware, status_saver: StatusSaver):
        self._logger = Logger()
        self._middleware = middleware
        self._status_saver = status_saver

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
    
    def initialize_system(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "..", "..", "config",  "ui_config.json")
        with open(json_directory, 'r') as json_file:
            try:
                data = json.load(json_file)  # Load the JSON data
                # Process the JSON data (replace this with your logic)
                self.add_panels(data)

                self._logger.info(f"Processing file: {json_directory}")
            except json.JSONDecodeError as e:
                self._logger.error(f"VisualizationWebSocketHandler:: Error processing file {json_directory}: {e}")

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
                self.add_panel(panel_info, group_name)

    def add_panel(self, panel_info, group_name) -> Union[bool, str]:
        panel = Panel(panel_info)

        if group_name not in self._panels_info:
            return False, "Add panel error, no group to add"

        result, message = self._status_saver.add_new_reading(panel._topic, panel._gateway)

        if result:
            self._panels_info[group_name].append(panel)
            self.update_ui_file()

        return result, message
    
    def add_panel_command(self, command):
        data = command["data"]

        result, message = self.add_panel(data, data["group"])

        if result:
            self._middleware.send_command_answear( result, self._panels_info[data["group"]][-1], command["requestId"])
        else:
            self._middleware.send_command_answear( result, message, command["requestId"])
        
    
    def remove_panel(self, panel_id) -> Union[bool, str]:
        for panels in self._panels_info.values():
            for idx, panel in enumerate(panels):
                if panel._id == panel_id:
                    result, message = self._status_saver.drop_reading_command(panel._topic, panel._gateway)
                    if result:
                        del panels[idx]
                        self.update_ui_file()
                    
                    return result, message
        
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

    def update_ui_file(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, "..", "..", "config",  "ui_config.json")

        obj = self.create_object_from_panels_info()

        with open(json_directory, 'w') as json_file:
            json_file.write( json.dumps(obj))