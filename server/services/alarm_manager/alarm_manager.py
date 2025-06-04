from support.logger import Logger
import queue
import uuid
from dataModules.alarm import Alarm
from middleware.middleware import ClientMiddleware
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

        self.id = str(uuid.uuid4())
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

    def initialize_commands(self):
        commands = {
            AlarmManagerCommands.REMOVE_ALARM: self.remove_alarm_command,
            AlarmManagerCommands.ADD_ALARM: self.add_alarm_command,
            AlarmManagerCommands.GET_ALARMS: self.get_alarm_command
            }
        self._middleware.add_commands(commands)
    
    def add_check_status(self, status_info):
        try:
            self._check_queue.put(status_info)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_check_status: Error adding data to queue {e}")

    def get_alarm_command(self, command):
        alarms, result = self._config_storage.get_alarm_info()
        if result:
            self._middleware.send_command_answear( result, alarms, command["requestId"])
        else:
            self._middleware.send_command_answear( result, 
                                                  f"Unable to get alarms", 
                                                  command["requestId"])

    def add_alarm_command(self, command):
        result = self.add_alarm(command)
        
        if result._id != '':
            self._middleware.send_command_answear( True, result.to_json(), command["requestId"])
        else:
            self._middleware.send_command_answear( result, 
                                                  f"Unable to add alarm", 
                                                  command["requestId"])

    def add_alarm(self, alarm_info):
        try:
            alarm = Alarm(alarm_info['data'])
            id = self._config_storage.add_alarm(alarm)
            if id != -1:
                alarm._id = id
                self.setup_alarm(alarm)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return alarm

    def setup_alarm(self, alarm: Alarm):
        if alarm._topic not in self._status_subscribers:
            self._status_subscribers[alarm._topic] = StatuSubscribers(self.add_check_status, 
                                                                      alarm._topic, 
                                                                      self.id + str(self._subscriptions_add))
            self._middleware.add_subscribe_to_status(self._status_subscribers[alarm._topic], alarm._topic)
            self._subscriptions_add+=1

            self._alarms_info[alarm._topic] = []

        self._alarms_info[alarm._topic].append(alarm)

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
                topic = alarm_info[0]["topic"]
                if topic in self._alarms_info:

                    result = self._config_storage.remove_alarm(alarm_id)
                    if result:
                        self.remove_alarm_internal_info(topic, alarm_id)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return True

    def remove_alarm_internal_info(self, topic, alarm_id):
        if( topic in self._alarms_info ):
            alarm = next((obj for obj in self._alarms_info[topic] if obj._id == alarm_id), None)
            if alarm:
                self._alarms_info[topic].remove(alarm)
                if len(self._alarms_info[topic]) == 0:
                    self._middleware.remove_subscribe_from_status(self._status_subscribers[alarm._topic], alarm._topic)
                    del self._alarms_info[topic]
    
    

                