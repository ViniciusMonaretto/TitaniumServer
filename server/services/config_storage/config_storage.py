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
from .config_storage_commands import Commands

DB_CONFIG = "db_status_saves.json"
DB_NAME = "titanium_server_db.db"

class ConfigStorage(ServiceInterface):
    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self.id = str(uuid.uuid4())
        self._subscriptions_add = 0
        self._middleware = middleware

        self.initialize_commands()

        self.create_db()

        self._logger.info("ConfigStorage initialized")
        
    def get_panel_topic(self, gateway, status_name):
        return gateway + "/" + status_name
    
    def initialize_commands(self):
        commands = {
            Commands.GET_ALARM_INFO: self.get_alarm_info_command
            }
        self._middleware.add_commands(commands)

    def create_db(self):
        try:
            conn = sqlite3.connect(DB_NAME) 
            cursor = conn.cursor()

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
            message = f"ConfigStorage::create_db: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message
        
    def drop_reading(self, topic, gateway, panel_id) ->  Union[bool, str]: 
        if not self.remove_panel(panel_id):
            return False, "Panel not found on DB"
        self.remove_subscription_to_status(gateway, topic)
        return True, ""
        
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

    def get_alarm_info_command(self, command):
        alarms, result = self.get_alarm_info(command["id"], command["topic"])
        if(result):
            self._middleware.send_command_answear( alarms, "", command["requestId"])
        else:
            self._middleware.send_command_answear( [], "Error Getting Alarms", command["requestId"])
        

    def get_alarm_info(self, id = None, topic = None):
        rows = []
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            values = None

            where_clause = ""

            if id or topic:
                where_clause = " WHERE "
                if id:
                    where_clause += "id = ?"
                    values = (id)
                if topic:
                    where_clause += " AND " if id else ""
                    where_clause += "topic = ?"
                    values  = (values, topic) if values else (topic)

            table_command =  f"""SELECT *
                                 FROM Alarms""" + where_clause
            
            cursor.execute(table_command, values)
            rows = cursor.fetchall()
            result = True

        except Exception as e:
            self._logger.error(f"ConfigStorage::get_table_info_command: Error trying to fetch info from table {e}")
        finally:
            conn.close()
        
        return rows, result