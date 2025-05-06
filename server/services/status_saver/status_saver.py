import sqlite3
import pytz
from datetime import datetime
from typing import Union
from middleware.status_subscriber import StatuSubscribers
from middleware.middleware import ClientMiddleware
import uuid
import threading
import queue

from dataModules.panel import Panel
from dataModules.alarm import Alarm
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

        self.create_db()
        
        self._write_queue = queue.Queue()
        
        self._info_wrything_thread = threading.Thread(target=self.write_sensor_data_loop, daemon=True)
        self._info_wrything_thread.start()

        self._logger.info("StatusSaver initialized")
        
    def get_panel_topic(self, gateway, status_name):
        return gateway + "/" + status_name
    
    def initialize_commands(self):
        commands = {
            Commands.GET_SENSOR_INFO: self.get_sensor_info_command,
            Commands.ADD_NEW_READING: self.add_new_reading_command,
            Commands.DROP_READING: self.drop_reading_command,
            Commands.GET_ALARM_INFO: self.get_alarm_info_command
            }
        self._middleware.add_commands(commands)

    def create_db(self):
        try:
            conn = sqlite3.connect(DB_NAME) 
            cursor = conn.cursor()

            # === Create Table ===
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS SensorData (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL
            );
            """)

            # === Create Indexes ===
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_time ON SensorData(name, timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_time ON SensorData(timestamp);")
            conn.commit()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Panels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gateway TEXT NOT NULL,
                topic TEXT NOT NULL,
                color TEXT NOT NULL,
                panelGroup TEXT NOT NULL,
                sensorType TEXT NOT NULL
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                threshold REAL NOT NULL,
                isUpper BOOLEAN NOT NULL,
                panelId INTEGER NOT NULL,
                FOREIGN KEY (panelId) REFERENCES Panels (id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alarmId INTEGER NOT NULL,
                name TEXT NOT NULL,
                Timestamp REAL NOT NULL,
                FOREIGN KEY (alarmId) REFERENCES Alarms (id) ON DELETE CASCADE
            );
            """)

            conn.commit()
            
            conn.close()
        except Exception as e:
            message = f"StatusSaver::create_db: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message
        
    def drop_reading(self, topic, gateway, panel_id) ->  Union[bool, str]: 
        if not self.remove_panel(panel_id):
            return False, "Panel not found on DB"
        self.remove_subscription_to_status(gateway, topic)
        return True, ""

    def add_new_reading(self, topic: str, gateway: str) ->  Union[bool, str]:
        try:
            self.subscribe_to_status(gateway, topic)
            return True, ""
        
        except Exception as e:
            message = f"StatusSaver::add_new_reading: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message
        
    def add_panel(self, panel: Panel):
        new_id = -1
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Panels (name, gateway, topic, color, panelGroup, sensorType)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (panel._name, panel._gateway, panel._topic, panel._color, panel._group, panel._sensor_type))

            conn.commit()
            new_id = cursor.lastrowid

        except Exception as e:
            self._logger.error(f"Panel Add error: {e}" )
        finally:
            conn.close()
        return new_id
    
    def remove_panel(self, panel_id: int):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Delete the alarm
            cursor.execute("DELETE FROM Panels WHERE id = ?;", (panel_id,))
            conn.commit()

            if cursor.rowcount == 0:
                print(f"No panel found with id {panel_id}.")
            else:
                result = True

        except sqlite3.Error as e:
            self._logger.error(f"remove_panel error: {e}")
        finally:
            conn.close()
        return result
    
    def get_panels(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row  # So we can access columns by name
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Panels")
            rows = cursor.fetchall()

            panels = [dict(row) for row in rows]  # Convert each row to a dict
            return panels

        except sqlite3.Error as e:
            self._logger.error(f"Status_saver::get_panels: SQLite error: {e}" )
            return []
        finally:
            conn.close()
    
    def add_alarm(self, alarm: Alarm):
        new_id = -1
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute('''
                topic,
                threshold,
                isUpper,
                panelId
                VALUES (?, ?, ?, ?)
            ''', (alarm._topic, alarm._threshold, alarm._is_upper, alarm._panel_id))

            conn.commit()
            new_id = cursor.lastrowid

        except Exception as e:
            self._logger.error(f"Panel Add error: {e}" )
        finally:
            conn.close()
        return new_id
    
    def remove_alarm(self, alarm_id: int):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Enable foreign key support
            cursor.execute("PRAGMA foreign_keys = ON;")

            # Delete the alarm
            cursor.execute("DELETE FROM Alarms WHERE id = ?;", (alarm_id,))
            conn.commit()

            if cursor.rowcount == 0:
                print(f"No panel found with id {alarm_id}.")
            else:
                result = True

        except sqlite3.Error as e:
            self._logger.error(f"remove_alarm error: {e}")
        finally:
            conn.close()
        return result
    
    

    
    def drop_reading_command(self, command):
        result, message = self.drop_reading(command["data"]["topic"], command["data"]["gateway"], command["data"]["id"])
        self._middleware.send_command_answear( result, message, command["requestId"])
    
    def add_new_reading_command(self, command):
        data = command["data"]

        result, message = self.add_new_reading(data["topic"], data["gateway"])

        self._middleware.send_command_answear( result, message, command["requestId"])

    def get_alarm_info_command(self, command):
        alarms, result = self.get_alarm_info()
        if(result):
            self._middleware.send_command_answear( alarms, "", command["requestId"])
        else:
            self._middleware.send_command_answear( [], "Error Getting Alarms", command["requestId"])
        

    def get_alarm_info(self):
        rows = []
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            table_command =  f"""SELECT *
                                 FROM Alarms""" 
            
            cursor.execute(table_command)
            rows = cursor.fetchall()
            result = True

        except Exception as e:
            self._logger.error(f"StatusSaver::get_table_info_command: Error trying to fetch info from table {e}")
        finally:
            conn.close()
        
        return rows, result


    def get_sensor_info_command(self, command):
        data = command["data"]

        sensor_infos = data["sensorInfos"]

        date_command = ""

        placeholders = ""
        values = []

        for index, info in enumerate(sensor_infos):
            table_name = info["topic"]
            gateway = info["gateway"]
            if(gateway):
                table_name = gateway + '-' + table_name
            
            values = values + [table_name]
            placeholders += '?'
            if(index != len(sensor_infos) - 1):
                placeholders += ', '
        
        if("beginDate" in data):
            dt = datetime.strptime( data["beginDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
            date_command += " AND timestamp >= ?"
            values = values + [dt.timestamp()]

            if("endDate" in data):
                date_command += " AND timestamp <= ?"
                values = values + [data["endDate"]]

        data_out = {'info': {}}

        result = True

        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            table_command =  f"""SELECT name, timestamp, value
                                 FROM SensorData
                                 WHERE name IN ({placeholders})""" + date_command
            
            cursor.execute(table_command, values)
            rows = cursor.fetchall()

            conn.commit()

            local_tz = pytz.timezone("America/Sao_Paulo")

            for sensor_name, timestamp, value in rows:
                if sensor_name not in data_out['info']:
                    data_out['info'][sensor_name] = []
                tm = datetime.fromtimestamp(timestamp, local_tz)
                data_out['info'][sensor_name].append({'timestamp': tm.isoformat(), 'value': value})
            data_out['requestId'] = data['websocketId']
        except Exception as e:
            self._logger.error(f"StatusSaver::get_table_info_command: Error trying to fetch info from table {e}")
            result = False
        finally:
            conn.close()

        self._middleware.send_command_answear( result, data_out, command["requestId"])
    
    def subscribe_to_status(self, gateway, status_name):
        topic = self.get_panel_topic(gateway, status_name)
        if(not topic in self._status_subscribers):
            self._status_subscribers[topic] = StatuSubscribers(self.add_sensor_data_to_queue, topic, self.id + str(self._subscriptions_add))
            self._middleware.add_subscribe_to_status(self._status_subscribers[topic], topic)
            self._subscriptions_add+=1

    def remove_subscription_to_status(self, gateway, status_name):
        topic = self.get_panel_topic(gateway, status_name)
        if(topic in self._status_subscribers):
            self._middleware.remove_subscribe_from_status(self._status_subscribers[topic], topic)
            del self._status_subscribers[topic]
    
    def get_sensor_full_name(self, status_info):
        stat_info = status_info['name'].split('/')
        sub_info = status_info['subStatusName'].split('/')

        if(sub_info[0] == '*'):
            return stat_info[1]
        else:
            return stat_info[0] + '-' + stat_info[1]
        
    def add_sensor_data_to_queue(self, status_info):
        try:
            self._write_queue.put(status_info)
        except Exception as e:
            self._logger.error(f"StatusSaver::add_sensor_data_to_queue: Error adding data to queue {e}")

    def write_sensor_data_loop(self):
        while True:
            sensor_infos = []
            while not self._write_queue.empty():
                try:
                    sensor_info = self._write_queue.get(timeout=1)
                    info = sensor_info['data']
                    status_name = self.get_sensor_full_name(sensor_info)
                    timestamp = datetime.fromisoformat(info["timestamp"])
                    
                    sensor_infos.append((timestamp.timestamp(), status_name, info["data"]))
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._logger.error(f"StatusSaver::write_sensor_data_loop: Error getting data from write queue {e}")
                    break
            
            if len(sensor_infos) > 0:
                self.save_sensor_data_on_db(sensor_infos)
            threading.Event().wait(1)
            
            

    
    def save_sensor_data_on_db(self, status_infos):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.executemany(f'INSERT INTO "SensorData" (timestamp, name, value) VALUES (?, ?, ?)', status_infos)

            conn.commit()
        except Exception as e:
            self._logger.error(f"StatusSaver::save_sensor_data_on_db: Error saving data on db {e}")
        finally:
            conn.close()