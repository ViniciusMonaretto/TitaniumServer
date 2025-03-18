import sqlite3
import json
import os
from datetime import datetime
from typing import Union
from middleware.status_subscriber import StatuSubscribers
from middleware.middleware import ClientMiddleware
import uuid

from support.logger import Logger
from ..service_interface import ServiceInterface
from .status_saver_commands import Commands

DB_CONFIG = "db_status_saves.json"
DB_NAME = "titanium_server_db.db"

class StatusSaver(ServiceInterface):
    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self.id = str(uuid.uuid4())
        self._subscriptions_add = 0
        self._status_subscribers = {}
        self._middleware = middleware

        self.initialize_commands()

        self._logger.info("StatusSaver initialized")
        
    def get_panel_topic(self, gateway, status_name):
        return gateway + "/" + status_name
    
    def initialize_commands(self):
        commands = {
            Commands.GET_TABLE_INFO: self.get_table_info_command,
            Commands.ADD_NEW_TABLE: self.add_new_table_command,
            Commands.DROP_TABLE: self.drop_table_command
            }
        self._middleware.add_commands(commands)

    def drop_table(self, topic, gateway) ->  Union[bool, str]: 
        conn = sqlite3.connect(DB_NAME) 
        cursor = conn.cursor()

        table_name = gateway + '-' + topic

        result = False
        message = ""

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone():
            quoted_table_name = f'"{table_name}"'
            cursor.execute(f"DROP TABLE {quoted_table_name}")
            conn.commit()

            self.remove_subscription_to_status(gateway, topic)

            self._logger.info(f"Table '{table_name}' has been dropped.")
            result = True
        else:
            message = f"Table '{table_name}' does not exist."
            self._logger.error(message)

        conn.close()
        return result, message

    def add_new_table(self, topic: str, gateway: str) ->  Union[bool, str]:
        try:
            table_name = gateway + '-' + topic
            conn = sqlite3.connect(DB_NAME) 
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS '{table_name}' (id INTEGER PRIMARY KEY AUTOINCREMENT,value NUMBER,timestamp DATE)")
                conn.commit()
            self.subscribe_to_status(gateway, topic)
            
            conn.close()
            return True, ""
        except Exception as e:
            message = f"StatusSaver::add_new_table: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message
    
    def drop_table_command(self, command):
        result, message = self.drop_table(command["data"]["topic"], command["data"]["gateway"])
        self._middleware.send_command_answear( result, message, command["requestId"])
    
    def add_new_table_command(self, command):
        data = command["data"]

        result, message = self.add_new_table(data["topic"], data["gateway"])

        self._middleware.send_command_answear( result, message, command["requestId"])

    def get_table_info_command(self, command):
        data = command["data"]

        table_name = data["table"]
        gateway = data["gateway"]
        timestamp = data['timestamp']
        if(gateway):
            table_name = gateway + '-' + table_name

        data_out = {'info': [], 'tableName': table_name}

        result = True

        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            

            table_command = f'SELECT * FROM "{table_name}"'

            values = None
            if(timestamp):
                table_command += " WHERE timestamp >= ?"
                values = (timestamp,)

            cursor.execute(table_command, values)

            rows = cursor.fetchall()

            data_out['info']=[dict(row) for row in rows]

            conn.commit()
        except Exception as e:
            self._logger.error(f"StatusSaver::get_table_info_command: Error trying to fetch info from table {e}")
            result = False
        finally:
            conn.close()

        self._middleware.send_command_answear( result, data_out, command["requestId"])
    
    def subscribe_to_status(self, gateway, status_name):
        topic = self.get_panel_topic(gateway, status_name)
        if(not topic in self._status_subscribers):
            self._status_subscribers[topic] = StatuSubscribers(self.save_status_on_db, topic, self.id + str(self._subscriptions_add))
            self._middleware.add_subscribe_to_status(self._status_subscribers[topic], topic)
            self._subscriptions_add+=1

    def remove_subscription_to_status(self, gateway, status_name):
        topic = self.get_panel_topic(gateway, status_name)
        if(topic in self._status_subscribers):
            self._middleware.remove_subscribe_from_status(self._status_subscribers[topic], topic)
            del self._status_subscribers[topic]
    
    def get_table_name(self, status_info):
        stat_info = status_info['name'].split('/')
        sub_info = status_info['subStatusName'].split('/')

        if(sub_info[0] == '*'):
            return stat_info[1]
        else:
            return stat_info[0] + '-' + stat_info[1]

    def save_status_on_db(self, status_info):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        status_name = self.get_table_name(status_info)

        status_obj = status_info['data']

        cursor.execute(f'INSERT INTO "{status_name}" (timestamp, value) VALUES (?, ?)', 
                      (datetime.fromisoformat(status_obj["timestamp"]), status_obj["data"]))

        conn.commit()
        conn.close()