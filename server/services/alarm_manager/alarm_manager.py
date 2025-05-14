from logging import Logger
import queue
import uuid
from server.dataModules.alarm import Alarm
from server.middleware.middleware import ClientMiddleware
from server.middleware.status_subscriber import StatuSubscribers
from server.services.alarm_manager.alarm_manager_commands import AlarmManagerCommands
from server.services.config_storage.config_storage import ConfigStorage
from ..service_interface import ServiceInterface

class AlarmManager(ServiceInterface):
    _alarms_info: dict[str: Alarm] = {}
    _status_subscribers: dict[str: StatuSubscribers]

    def __init__(self, middleware: ClientMiddleware, status_saver: ConfigStorage):
        self._logger = Logger()
        self._middleware = middleware
        self._status_saver = status_saver

        self.id = str(uuid.uuid4())
        self._subscriptions_add = 1

        self._check_queue = queue.Queue()

        self.initialize_commands()
        self.initialize_system()

        self._logger.info("AlarmManager initialized")

    def initialize_system(self):
        alarms, result = self._status_saver.get_alarm_info()
        if result:
            for alarm_info in alarms:
                self.setup_alarm(Alarm(alarm_info))

    def initialize_commands(self):
        commands = {
            AlarmManagerCommands.REMOVE_ALARM: self.add_panel_command,
            AlarmManagerCommands.ADD_ALARM: self.remove_panel_command,
            }
        self._middleware.add_commands(commands)
    
    def add_check_status(self, status_info):
        try:
            self._check_queue.put(status_info)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_check_status: Error adding data to queue {e}")

    def add_alarm(self, alarm_info):
        try:
            alarm = Alarm(alarm_info)
            id = self._status_saver.add_alarm(alarm)
            if id != -1:
                alarm._id = id
                self.setup_alarm(alarm)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return True

    def setup_alarm(self, alarm: Alarm):
        self._alarms_info[alarm._id] = alarm

        self._status_subscribers[alarm._topic] = StatuSubscribers(self.add_check_status, 
                                                                  alarm._topic, 
                                                                  self.id + str(self._subscriptions_add))
        self._middleware.add_subscribe_to_status(self._status_subscribers[alarm._topic], alarm._topic)

        self._subscriptions_add+=1

    def remove_alarm(self, alarm_id):
        if alarm_id not in self._alarms_info:
            return False
        try:
            result = self._status_saver.remove_alarm(alarm_id)
            if result:
                self.remove_alarm_internal_info(alarm_id)
        except Exception as e:
            self._logger.error(f"AlarmManager::add_alarm error: {e}")
        
        return True

    def remove_alarm_internal_info(self, alarm_id):
        if( alarm_id in self._alarms_info ):
            alarm = self._alarms_info[alarm_id]
            self._middleware.remove_subscribe_from_status(self._status_subscribers[alarm._topic], alarm._topic)
            del self._alarms_info[alarm_id]
    
    

                