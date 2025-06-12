from datetime import datetime
import threading
from dataModules.sensor_info import SensorInfo
from dataModules.event import EventModel
from support.logger import Logger
import queue
import uuid
from dataModules.alarm import Alarm, AlarmType
from middleware.client_middleware import ClientMiddleware
from middleware.status_subscriber import StatuSubscribers
from services.alarm_manager.alarm_manager_commands import AlarmManagerCommands
from services.config_storage.config_storage import ConfigStorage
from ..service_interface import ServiceInterface

class AlarmManager(ServiceInterface):
    _alarms_info: dict[str, list[Alarm]] = {}
    _status_subscribers: dict[str: StatuSubscribers] = {}

    def __init__(self, middleware: ClientMiddleware, config_storage: ConfigStorage):
        self._logger = Logger()
        self._middleware = middleware
        self._config_storage = config_storage

        self._subscriptions_add = 1

        self._check_queue = queue.Queue()

        self.initialize_commands()
        self.initialize_system()

        self._logger.info("AlarmManager initialized")

    def initialize_system(self):
        alarms, result = self._config_storage.get_alarm_info()
        if result:
            for alarm_info in alarms:
                self.setup_alarm(Alarm(alarm_info))
        
        self._alarm_check_thread = threading.Thread(target=self.alarm_check_thread, daemon=True)
        self._alarm_check_thread.start()

    def initialize_commands(self):
        commands = {
            AlarmManagerCommands.REMOVE_ALARM: self.remove_alarm_command,
            AlarmManagerCommands.ADD_ALARM: self.add_alarm_command,
            AlarmManagerCommands.GET_ALARMS: self.get_alarm_command
            }
        self._middleware.add_commands(commands)

    def check_if_alarm_should_trigger(self, alarm: Alarm, value):
        alarm_type = alarm.type
        if alarm_type == AlarmType.Equal:
            return value == alarm.threshold
        if alarm_type == AlarmType.Higher:
            return value > alarm.threshold
        if alarm_type == AlarmType.Lower:
            return value < alarm.threshold

    def alarm_check_thread(self):
        while True:
            events_to_add: list[EventModel] = []
            while not self._check_queue.empty():
                try:
                    sensor_info: SensorInfo = self._check_queue.get(timeout=1)
                    sensor_info.timestamp = datetime.fromisoformat(sensor_info.timestamp)

                    topic = sensor_info.sensor_full_topic.replace('-', '/')

                    for alarm in self._alarms_info[topic]:
                        if self.check_if_alarm_should_trigger(alarm, sensor_info.value):
                            evt = EventModel(alarm.id, 
                                             alarm.panel_id, 
                                             sensor_info.timestamp,
                                             sensor_info.value)
                            evt.name = alarm.name
                            events_to_add.append(evt)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._logger.error(f"SensorDataStorage::write_sensor_data_loop: Error getting data from write queue {e}")
                    break
            if len(events_to_add) > 0:
                if self._config_storage.add_event_array(events_to_add):
                    self._send_event_status(events_to_add)
        
            threading.Event().wait(1)
    
    def _send_event_status(self, event_list: list[EventModel]):
        for event_model in event_list:
            self._middleware.send_status("Alarm/newevent", event_model.to_json())

    def add_check_status(self, status_info):
        try:
            self._check_queue.put(SensorInfo(status_info["subStatusName"].replace('/', '-'),
                                             datetime.fromisoformat(status_info["data"]["timestamp"]),
                                             status_info["data"]["data"]))
        except Exception as e:
            self._logger.error(f"AlarmManager::add_check_status: Error adding data to queue {e}")

    def get_alarm_command(self, command):
        alarms, result = self._config_storage.get_alarm_info()
        if result:
            self._middleware.send_command_answear( result, alarms, command["requestId"])
        else:
            self._middleware.send_command_answear( result, 
                                                  "Unable to get alarms", 
                                                  command["requestId"])

    def add_alarm_command(self, command):
        result = self.add_alarm(command)
        
        if result.id != '':
            self._middleware.send_command_answear( True, result.to_json(), command["requestId"])
        else:
            self._middleware.send_command_answear( result, 
                                                  "Unable to add alarm", 
                                                  command["requestId"])

    def add_alarm(self, alarm_info):
        try:
            alarm = Alarm(alarm_info['data'])
            alarm_id = self._config_storage.add_alarm(alarm)
            if alarm_id != -1:
                alarm.id = alarm_id
                self.setup_alarm(alarm)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return alarm

    def setup_alarm(self, alarm: Alarm):
        topic = alarm.topic.replace("-","/")
        if topic not in self._status_subscribers:
            self._status_subscribers[topic] = StatuSubscribers(self.add_check_status, topic)
            self._middleware.add_subscribe_to_status(self._status_subscribers[topic], topic)
            self._subscriptions_add+=1

            self._alarms_info[topic] = []

        self._alarms_info[topic].append(alarm)

    def remove_alarm_command(self, command):
        result = self.remove_alarm(command['data']["id"])
        if result:
            self._middleware.send_command_answear( result, command['data']["id"], command["requestId"])
        else:
            self._middleware.send_command_answear( result, f"Unable to remove alarm {command['sensorId']}", 
                                                  command["requestId"])

    def remove_alarm(self, alarm_id):
        try:
            alarm_info, result = self._config_storage.get_alarm_info(alarm_id)
            if len(alarm_info) > 0:
                topic = alarm_info[0]["topic"].replace("-","/")
                if topic in self._alarms_info:

                    result = self._config_storage.remove_alarm(alarm_id)
                    if result:
                        self.remove_alarm_internal_info(topic, alarm_id)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return True

    def remove_alarm_internal_info(self, topic_in: str, alarm_id):
        topic = topic_in.replace("-","/")
        if( topic in self._alarms_info ):
            alarm = next((obj for obj in self._alarms_info[topic] if obj.id == alarm_id), None)
            if alarm:
                self._alarms_info[topic].remove(alarm)
                if len(self._alarms_info[topic]) == 0:
                    self._middleware.remove_subscribe_from_status(self._status_subscribers[topic], topic)
                    del self._alarms_info[topic]
    
    

                