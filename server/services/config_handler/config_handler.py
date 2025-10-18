import json
import os
import threading
from datetime import datetime, timedelta
from middleware.client_middleware import ClientMiddleware

from dataModules.panel import Panel
from middleware.status_subscriber import StatuSubscribers
from dataModules.alarm import Alarm, AlarmType
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from dataModules.panel_group import PanelGroup
from dataModules.gateway import GatewayStatus
from services.alarm_manager.alarm_manager import AlarmManager
from services.sensor_data_storage.sensor_data_storage import SensorDataStorage
from support.logger import Logger


from .config_handler_command import ConfigHandlerCommands
from ..service_interface import ServiceInterface

from ..config_storage.config_storage import ConfigStorage

DB_CONFIG = "db_status_saves.json"
DB_NAME = "titanium_server_db.db"


class ConfigHandler(ServiceInterface):
    _panel_groups: dict[int, PanelGroup] = {}
    _status_subscribers = {}
    _panel_groups_lock: threading.Lock = None

    def __init__(
        self,
        middleware: ClientMiddleware,
        config_storage: ConfigStorage,
        sensor_data_storage: SensorDataStorage,
        alarm_manager: AlarmManager,
    ):
        self._logger = Logger()
        self._middleware = middleware
        self._config_storage = config_storage
        self._sensor_data_storage = sensor_data_storage
        self._alarm_manager = alarm_manager
        self._panel_groups_lock = threading.Lock()

        self.initialize_commands()
        self.initialize_system()

        self._logger.info("ConfigHandler initialized")

    def initialize_commands(self):
        commands = {
            ConfigHandlerCommands.ADD_PANEL: self.add_panel_command,
            ConfigHandlerCommands.REMOVE_PANEL: self.remove_panel_command,
            ConfigHandlerCommands.GET_PANEL_LIST: self.get_panels_list_command,
            ConfigHandlerCommands.UPDATE_PANEL_FUNCTIONALITIES: self.update_panel_functions_command,
            ConfigHandlerCommands.ADD_PANEL_GROUP: self.add_panel_group_command,
            ConfigHandlerCommands.REMOVE_PANEL_GROUP: self.remove_panel_group_command,
            ConfigHandlerCommands.UPDATE_PANEL_GROUP: self.update_panel_group_command,
        }
        self._middleware.add_commands(commands)

    def read_default_config(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(
            script_directory, "..", "..", "config", "ui_config.json"
        )
        with open(json_directory, "r", encoding="utf-8") as json_file:
            try:
                data = json.load(json_file)  # Load the JSON data
                # Process the JSON data (replace this with your logic)
                self.initialize_panels_from_config(data)

                self._logger.info(f"Processing file: {json_directory}")
            except json.JSONDecodeError as e:
                self._logger.error(
                    f"VisualizationWebSocketHandler:: Error processing file {json_directory}: {e}"
                )

    def initialize_panels_from_db(self, panels_infos, groups_infos):
        for group_info in groups_infos:
            self.add_panel_group(group_info["name"])
        for panel_info in panels_infos:
            self.add_panel(panel_info)

    def initialize_system(self):
        groups_infos = self._config_storage.get_panel_groups()
        panels_infos = self._config_storage.get_panels()
        if len(panels_infos) == 0 or len(groups_infos) == 0:
            self.read_default_config()
        else:
            self.initialize_panels_from_db(panels_infos, groups_infos)

    def update_calibration_from_gateway_status(self, panels: list[{
        "status": str,
        "gain": float,
        "offset": float,
        "topic": str,
        "indicator": str
    }]):
        for panel_info in panels:
            panel: Panel = self._find_panel_from_topic(
                panel_info.topic, str(panel_info.indicator), panel_info.gateway)
            if panel:
                panel.offset = panel_info.offset
                panel.gain = panel_info.gain
                self._config_storage.update_panel(panel)
        self.send_ui_update_action(False)

    def calibration_update_received(self, status_info, group_id, index):
        data = status_info["data"]

        with self._panel_groups_lock:
            panel: Panel = self._panel_groups[group_id].panels[index]
            panel.offset = data.offset
            panel.gain = data.gain
        self._config_storage.update_panel(panel)
        self.send_ui_update_action(True)

    def subscribe_to_status(self, gateway, status_name, indicator, group_id, index):
        topic = ClientMiddleware.get_calibrate_topic(
            gateway, status_name, indicator)
        if not topic in self._status_subscribers:
            self._status_subscribers[topic] = StatuSubscribers(
                lambda status_info: self.calibration_update_received(
                    status_info, group_id, index
                ),
                topic,
            )
            self._middleware.add_subscribe_to_status(
                self._status_subscribers[topic], topic
            )

    def _find_panel_from_id(self, panel_id):
        with self._panel_groups_lock:
            for group_id in self._panel_groups:
                panel: Panel | None = next(
                    (item for item in self._panel_groups[group_id].panels
                     if item.id == panel_id),
                    None,
                )
                if panel != None:
                    return panel

        return None

    def initialize_panels_from_config(self, panels_info):
        for group_id in panels_info:
            if group_id not in self._panel_groups:
                self.add_panel_group(group_id)

            for panel_info in panels_info[group_id]:
                self.add_panel(panel_info)

    def add_panel(self, panel_info) -> tuple[bool, str]:
        result = False
        message = ""
        panel = Panel(panel_info)

        group_id = panel.group_id

        index = -1
        if not panel.id:
            index = self._config_storage.add_panel(panel)
        else:
            index = panel.id
        if index != -1:
            panel.id = index
            subscription_result = self._sensor_data_storage.add_new_subscription(
                panel.topic, panel.gateway, panel.indicator
            )
            if isinstance(subscription_result, tuple):
                result, message = subscription_result
            else:
                result = subscription_result
                message = "Subscription result"

            if result:
                with self._panel_groups_lock:
                    self._panel_groups[group_id].panels.append(panel)
                    panel_index = len(self._panel_groups[group_id].panels) - 1
                self.subscribe_to_status(
                    panel.gateway,
                    panel.topic,
                    panel.indicator,
                    group_id,
                    panel_index,
                )

        return result, message

    def add_panel_command(self, command):
        data = command["data"]

        result, message = self.add_panel(data)

        if result:
            with self._panel_groups_lock:
                last_panel = self._panel_groups[data["group"]].panels[-1]
            self._middleware.send_command_answear(
                result, last_panel, command["requestId"]
            )
        else:
            self._middleware.send_command_answear(
                result, message, command["requestId"])

    def update_panel_functions_command(self, command):
        try:
            self.update_panel_functions(command["data"])
            self._middleware.send_command_answear(
                True, {}, command["requestId"])
        except Exception as e:
            self._middleware.send_command_answear(
                False, f"{e}", command["requestId"])

    def update_panel_functions(self, update_panel_info):
        gain = update_panel_info["gain"]
        offset = update_panel_info["offset"]
        max_alarm = (
            update_panel_info["maxAlarm"] if "maxAlarm" in update_panel_info else None
        )
        min_alarm = (
            update_panel_info["minAlarm"] if "minAlarm" in update_panel_info else None
        )
        panel_id = update_panel_info["panelId"]
        panel = self._find_panel_from_id(panel_id)

        if panel:
            panel.max_alarm = self.handle_change_panel_alarm(
                panel, panel.max_alarm, max_alarm, True
            )
            panel.min_alarm = self.handle_change_panel_alarm(
                panel, panel.min_alarm, min_alarm, False
            )
            panel.color = update_panel_info["color"]
            panel.name = update_panel_info["name"]
            panel.multiplier = update_panel_info["multiplier"]
            if not self._config_storage.update_panel(panel):
                self._logger.error(
                    f"ConfigHandler::update_panel_functions: Error saving panel update {panel.id}")
            if gain != panel.gain or offset != panel.offset:
                self._middleware.send_command(
                    MqttCommands.CALIBRATION, update_panel_info
                )
            else:
                self.send_ui_update_action()

    def handle_change_panel_alarm(
        self, panel: Panel, alarm: Alarm, new_alarm_value: float, is_max_alarm: bool
    ):
        if alarm == None and new_alarm_value != None:
            alarm_info = {
                "name": str(panel.id) + ("max" if is_max_alarm else "min"),
                "topic": ClientMiddleware.get_status_topic(
                    panel.gateway, panel.topic, panel.indicator
                ),
                "threshold": new_alarm_value,
                "type": AlarmType.Higher if is_max_alarm else AlarmType.Lower,
                "panelId": panel.id,
            }
            return self._alarm_manager.add_alarm(alarm_info)
        elif alarm != None and new_alarm_value == None:
            self._alarm_manager.remove_alarm(alarm.id)
            return None
        elif alarm != None and alarm.threshold != new_alarm_value:
            return self._alarm_manager.change_alarm_threshold(
                alarm.id, new_alarm_value, ClientMiddleware.get_status_topic(
                    panel.gateway, panel.topic, panel.indicator
                )
            )

        # If alarm exists and new value is the same, return existing alarm unchanged
        return alarm

    def remove_panel(self, panel_id) -> tuple[bool, str]:
        try:
            with self._panel_groups_lock:
                for group in self._panel_groups.values():
                    for idx, panel in enumerate(group.panels):
                        if panel.id == panel_id:
                            wait_flag = threading.Event()
                            self._sensor_data_storage.erase_sensor_info(
                                [
                                    ClientMiddleware.get_calibrate_topic(
                                        panel.gateway, panel.topic, panel.indicator
                                    )
                                ],
                                None,
                                None,
                                lambda a, b: wait_flag.set(),
                            )
                            wait_flag.wait(180)

                            result = self._config_storage.remove_panel(
                                panel_id)

                            if result:
                                self.remove_panel_subscription(
                                    group.panels[idx])
                                del group.panels[idx]
                                return True, "Painél Removido"
        except Exception as e:
            self._logger.error(
                f"ConfigHandler::remove_panel: Error while removing panel {e}"
            )

        return False, "Remove panel error: Panel not found"

    def remove_panel_subscription(self, panel):
        topic = ClientMiddleware.get_calibrate_topic(
            panel.gateway, panel.topic, panel.indicator
        )
        if topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(
                self._status_subscribers[topic], topic
            )
            del self._status_subscribers[topic]

    def remove_panel_command(self, command):
        data = command["data"]

        result, message = self.remove_panel(data["id"])

        if result:
            self._middleware.send_command_answear(
                result, {}, command["requestId"])
        else:
            self._middleware.send_command_answear(
                result, message, command["requestId"])

    def get_topic_mappings(self):
        """Get topic to name and type mappings for report generation."""
        topic_to_name = {}
        topic_to_type = {}

        with self._panel_groups_lock:
            for group in self._panel_groups.values():
                for panel in group.panels:
                    full_topic = f"{panel.gateway}-{panel.topic}-{panel.indicator}"
                    topic_to_name[full_topic] = panel.name
                    topic_to_type[full_topic] = panel.sensor_type

        return (topic_to_name, topic_to_type)

    def create_object_from_panels_info(self, calibrate_update=False):
        obj = {}
        current_time = datetime.now()

        with self._panel_groups_lock:
            for group in self._panel_groups.values():
                panels_with_last_values = []
                for panel in group.panels:
                    panel_json = panel.to_json()

                    # Get the last value/active status from sensor data storage
                    topic = ClientMiddleware.get_status_topic(
                        panel.gateway, panel.topic, panel.indicator)
                    last_status = self._sensor_data_storage.get_last_status_for_topic(
                        topic)

                    if last_status:
                        if hasattr(last_status, 'value'):
                            panel_json["value"] = last_status.value
                        if hasattr(last_status, 'timestamp'):
                            # Check if timestamp is 5 minutes old
                            if isinstance(last_status.timestamp, datetime):
                                time_diff = current_time - last_status.timestamp
                                panel_json["isActive"] = False if time_diff > timedelta(
                                    minutes=5) else last_status.is_active

                    panels_with_last_values.append(panel_json)

                obj[str(group.id)] = {"panels": panels_with_last_values,
                                      "groupName": group.name,
                                      "groupId": group.id}

        return {"calibrateUpdate": calibrate_update, 'PanelsInfo': obj}

    def get_panels_list_command(self, command):
        self._middleware.send_command_answear(
            True, self.create_object_from_panels_info(), command["requestId"]
        )

    def send_ui_update_action(self, calibrate_update=False):
        self._middleware.send_status(
            "ui-update-*", self.create_object_from_panels_info(
                calibrate_update)
        )

    # Panel Groups
    def add_panel_group_command(self, command):
        data = command["data"]
        result, message = self.add_panel_group(data["name"])
        self._middleware.send_command_answear(
            result, {}, command["requestId"])

    def remove_panel_group_command(self, command):
        data = command["data"]
        result, message = self.remove_panel_group(data["id"])
        self._middleware.send_command_answear(
            result, {}, command["requestId"])

    def update_panel_group_command(self, command):
        data = command["data"]
        result, message = self.update_panel_group(data["id"], data["name"])
        self._middleware.send_command_answear(
            result, {}, command["requestId"])

    def add_panel_group(self, name):
        group_id = self._config_storage.add_panel_group(name)
        if group_id != -1:
            # Check if group already exists in memory
            with self._panel_groups_lock:
                if group_id not in self._panel_groups:
                    self._panel_groups[group_id] = PanelGroup(name, group_id)
                    return True, "Success"
                else:
                    return True, "Group already exists"
        return False, "Error adding panel group"

    def remove_panel_group(self, group_id):
        result = self._config_storage.remove_panel_group(group_id)
        if result:
            with self._panel_groups_lock:
                for panel in self._panel_groups[group_id].panels:
                    self.remove_panel_subscription(panel)

                del self._panel_groups[group_id]
            return True, "Success"
        return False, "Error removing panel group"

    def update_panel_group(self, group_id, name):
        result = self._config_storage.update_panel_group(group_id, name)
        if result:
            with self._panel_groups_lock:
                self._panel_groups[name] = self._panel_groups[group_id]
                del self._panel_groups[group_id]
            return True, "Success"
        return False, "Error updating panel group"

    def _find_panel_from_topic(self, topic, indicator, gateway):
        with self._panel_groups_lock:
            for group in self._panel_groups.values():
                for panel in group.panels:
                    if panel.topic == topic and panel.indicator == indicator and panel.gateway == gateway:
                        return panel
        return None
