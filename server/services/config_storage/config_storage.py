import sqlite3
from datetime import datetime
import uuid
import pytz
from middleware.client_middleware import ClientMiddleware

from dataModules.panel import Panel
from dataModules.alarm import Alarm, AlarmType
from dataModules.event import EventModel
from support.logger import Logger
from ..service_interface import ServiceInterface
from .config_storage_commands import ConfigStorageCommand

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

    def initialize_commands(self):
        commands = {
            ConfigStorageCommand.GET_ALARM_INFO: self.get_alarm_info_command,
            ConfigStorageCommand.GET_EVENTS_LIST: self.get_events_info_command
        }
        self._middleware.add_commands(commands)

    def create_db(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PanelsGroups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Panels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gateway TEXT NOT NULL,
                topic TEXT NOT NULL,
                color TEXT NOT NULL,
                panelGroupId INTEGER NOT NULL,
                indicator TEXT NOT NULL,
                sensorType TEXT NOT NULL,
                gain FLOAT,
                offset FLOAT,
                multiplier INTEGER,
                FOREIGN KEY (panelGroupId) REFERENCES PanelsGroups (id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Alarms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                topic TEXT NOT NULL,
                threshold REAL NOT NULL,
                type INTEGER NOT NULL,
                panelId INTEGER NOT NULL,
                FOREIGN KEY (panelId) REFERENCES Panels (id) ON DELETE CASCADE
            );
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alarmId INTEGER NOT NULL,
                panelId INTEGER NOT NULL,
                value FLOAT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (alarmId) REFERENCES Alarms (id) ON DELETE CASCADE
            );
            """)

            conn.commit()

            conn.close()
        except Exception as e:
            message = f"ConfigStorage::create_db: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message

    def add_panel(self, panel: Panel):
        new_id = -1
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Panels (name, gateway, topic, color, panelGroupId, indicator, sensorType, multiplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (panel.name, panel.gateway, panel.topic, panel.color, panel.group_id, panel.indicator, panel.sensor_type, panel.multiplier))

            conn.commit()
            new_id = cursor.lastrowid

        except Exception as e:
            self._logger.error(f"Panel Add error: {e}")
        finally:
            conn.close()
        return new_id

    def remove_panel(self, panel_id: int):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute("DELETE FROM Panels WHERE id = ?;", (panel_id,))
            conn.commit()

            if cursor.rowcount == 0:
                self._logger.warning(f"No panel found with id {panel_id}.")
            else:
                result = True

        except sqlite3.Error as e:
            self._logger.error(f"remove_panel error: {e}")
        finally:
            conn.close()
        return result

    def update_alarm(self, alarm: Alarm):
        result = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            update_query = """
                UPDATE Alarms
                SET
                    name = ?,
                    topic = ?,
                    threshold = ?,
                    type = ?,
                    panelId = ?,
                WHERE id = ?;
                """

            new_values = (
                alarm.name,
                alarm.topic,
                alarm.threshold,
                alarm.type,
                alarm.panel_id
            )

            cursor.execute(update_query, new_values)
            conn.commit()

            result = alarm

        except sqlite3.Error as e:
            self._logger.error(f"update_panel error: {e}")
        finally:
            conn.close()
        return result

    def update_panel(self, panel: Panel):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            update_query = """
                UPDATE Panels
                SET
                    name = ?,
                    gateway = ?,
                    topic = ?,
                    color = ?,
                    panelGroupId = ?,
                    indicator = ?,
                    sensorType = ?,
                    gain = ?,
                    offset = ?,
                    multiplier = ?
                WHERE id = ?;
                """

            new_values = (
                panel.name,           # name
                panel.gateway,        # gateway
                panel.topic,          # topic
                panel.color,                # color
                panel.group_id,             # panelGroupId
                panel.indicator,         # indicator
                panel.sensor_type,        # sensorType
                panel.gain,                  # gain
                panel.offset,                  # offset
                panel.multiplier,            # multiplier
                panel.id,                     # id (which row to update)
            )

            cursor.execute(update_query, new_values)
            conn.commit()

            result = True

        except sqlite3.Error as e:
            self._logger.error(f"update_panel error: {e}")
        finally:
            conn.close()
        return result

    def get_panels(self) -> list[dict]:
        panels: list[dict] = []
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row  # So we can access columns by name
            cursor = conn.cursor()

            query = """
                    WITH FirstAlarms AS (
                        SELECT
                            id AS alarmId,
                            name AS alarmName,
                            topic AS alarmTopic,
                            threshold,
                            type AS alarmType,
                            panelId,
                            ROW_NUMBER() OVER (PARTITION BY panelId, type ORDER BY id) as rn
                        FROM Alarms
                    )
                    SELECT
                        p.id AS panelId,
                        p.name AS panelName,
                        p.gateway,
                        p.topic AS panelTopic,
                        p.color,
                        p.panelGroupId,
                        p.indicator,
                        p.sensorType,
                        p.gain,
                        p.offset,
                        p.multiplier,

                        a.alarmId,
                        a.alarmName,
                        a.alarmTopic,
                        a.threshold AS alarmThreshold,
                        a.alarmType

                    FROM Panels p
                    LEFT JOIN FirstAlarms a ON p.id = a.panelId AND a.rn = 1

                    ORDER BY p.id, a.alarmType
                    """

            cursor.execute(query)
            rows = cursor.fetchall()

            last_panel_id = -1
            for row in rows:
                info = dict(row)

                if last_panel_id != info['panelId']:
                    panel = {
                        'id': info['panelId'],
                        'name': row['panelName'],
                        'gateway': row['gateway'],
                        'topic': row['panelTopic'],
                        'color': row['color'],
                        'panelGroupId': row['panelGroupId'],
                        'indicator': row['indicator'],
                        'sensorType': row['sensorType'],
                        'gain': row['gain'],
                        'offset': row['offset'],
                        'multiplier': row['multiplier'],
                    }
                    panels.append(panel)
                    last_panel_id = info['panelId']

                if row['alarmId'] is not None:
                    alarm = {
                        'id': info['alarmId'],
                        'name': info['alarmName'],
                        'topic': info['alarmTopic'],
                        'threshold': info['alarmThreshold'],
                        'type': info['alarmType'],
                        'panelId': info['panelId']
                    }
                    if info['alarmType'] == AlarmType.Higher:
                        panels[-1]['maxAlarm'] = alarm
                    elif info['alarmType'] == AlarmType.Lower:
                        panels[-1]['minAlarm'] = alarm

        except sqlite3.Error as e:
            self._logger.error(f"Status_saver::get_panels: SQLite error: {e}")
            return []
        finally:
            conn.close()
        return panels

    def add_alarm(self, alarm: Alarm):
        new_id = -1
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute('''
                INSERT INTO Alarms (
                name,
                topic,
                threshold,
                type,
                panelId)
                VALUES (?, ?, ?, ?, ?)
            ''', (alarm.name, alarm.topic, alarm.threshold, alarm.type, alarm.panel_id))

            conn.commit()
            new_id = cursor.lastrowid

        except Exception as e:
            self._logger.error(f"Alarm Add error: {e}")
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
        if (result):
            self._middleware.send_command_answear(
                alarms, "", command["requestId"])
        else:
            self._middleware.send_command_answear(
                [], "Error Getting Alarms", command["requestId"])

    def get_alarm_info(self, alarm_id=None, topic=None):
        rows = []
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            where_clause = ""
            values = []

            if alarm_id or topic:
                where_clause = " WHERE "
                conditions = []
                if alarm_id is not None:
                    conditions.append("id = ?")
                    values.append(alarm_id)
                if topic is not None:
                    conditions.append("topic = ?")
                    values.append(topic)
                where_clause += " AND ".join(conditions)

            table_command = """SELECT *
                                FROM Alarms""" + where_clause

            cursor.execute(table_command, tuple(values))
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
            result = True

        except Exception as e:
            self._logger.error(
                f"ConfigStorage::get_table_info_command: Error trying to fetch info from table {e}")
        finally:
            conn.close()

        return rows, result

    def get_events_info_command(self, command):
        data = command["data"]
        events, result = self.get_events_info()
        if (result):
            panel_id = data["panelId"] if "panelId" in data else None
            self._middleware.send_command_answear(
                result, {'events': events, 'panelId': panel_id}, command["requestId"])
        else:
            self._middleware.send_command_answear(
                result, "Error Getting Events", command["requestId"])

    def get_events_info(self, panel_id=None, alarm_id=None, limit=None):
        rows = []
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            where_clause = ""
            values = []

            if panel_id or alarm_id:
                where_clause = " WHERE "
                conditions = []
                if panel_id is not None:
                    conditions.append("Events.panelId = ?")
                    values.append(panel_id)
                if alarm_id is not None:
                    conditions.append("Events.alarmId = ?")
                    values.append(alarm_id)
                where_clause += " AND ".join(conditions)

            limit_caluse = ""
            if limit is not None:
                limit_caluse = f" LIMIT {limit}"

            table_command = """SELECT 
                                Events.alarmId,
                                Events.panelId,
                                Events.value,
                                Events.timestamp,
                                Alarms.Name
                                FROM Events
                                JOIN Alarms ON Alarms.id = Events.alarmId""" + where_clause + limit_caluse

            cursor.execute(table_command, tuple(values))
            rows = cursor.fetchall()
            rows = [dict(row) for row in rows]
            local_tz = pytz.timezone("America/Sao_Paulo")
            for row in rows:
                row["timestamp"] = datetime.fromtimestamp(
                    row["timestamp"], local_tz).isoformat()
            result = True
        except Exception as e:
            self._logger.error(
                f"ConfigStorage::get_events_info: Error trying to fetch info from table {e}")
        finally:
            conn.close()

        return rows, result

    def add_event_array(self, events: list[EventModel]):
        result = False
        conn: sqlite3.Connection | None = None
        try:
            event_data = [
                (e.alarm_id, e.panel_id, e.value, e.timestamp.timestamp())
                for e in events
            ]
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.executemany('''
                INSERT INTO Events (
                alarmId,
                panelId,
                value,
                timestamp)
                VALUES (?, ?, ?, ?)
            ''', event_data)

            conn.commit()
            result = True
        except Exception as e:
            self._logger.error(f"Event Add error: {e}")
        finally:
            if conn != None:
                conn.close()

        return result

    def remove_events(self, event_info):
        conn: sqlite3.Connection | None = None
        result = False
        try:
            # Connect to the database
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # Delete all rows from the Events table
            cursor.execute("DELETE FROM Events")

            # Commit changes and close connection
            conn.commit()
            result = True
        except Exception as e:
            self._logger.error(f"Event Add error: {e}")
        finally:
            if conn:
                conn.close()

        return result

    def add_panel_group(self, name: str):
        new_id = -1
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            # First check if a group with this name already exists
            cursor.execute('''
                SELECT id FROM PanelsGroups WHERE name = ?
            ''', (name,))

            existing_group = cursor.fetchone()
            if existing_group:
                # Group already exists, return its ID
                new_id = existing_group[0]
                self._logger.info(
                    f"PanelGroup '{name}' already exists with id {new_id}")
            else:
                # Group doesn't exist, create it
                cursor.execute('''
                    INSERT INTO PanelsGroups (name)
                    VALUES (?)
                ''', (name,))

                conn.commit()
                new_id = cursor.lastrowid

        except Exception as e:
            self._logger.error(f"PanelGroup Add error: {e}")
        finally:
            conn.close()
        return new_id

    def remove_panel_group(self, group_id: int):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            cursor.execute(
                "DELETE FROM PanelsGroups WHERE id = ?;", (group_id,))
            conn.commit()

            if cursor.rowcount == 0:
                self._logger.warning(
                    f"No panel group found with id {group_id}.")
            else:
                result = True

        except sqlite3.Error as e:
            self._logger.error(f"remove_panel_group error: {e}")
        finally:
            conn.close()
        return result

    def update_panel_group(self, group_id: int, name: str):
        result = False
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON;")

            update_query = """
                UPDATE PanelsGroups
                SET name = ?
                WHERE id = ?;
                """

            cursor.execute(update_query, (name, group_id))
            conn.commit()

            if cursor.rowcount == 0:
                self._logger.warning(
                    f"No panel group found with id {group_id}.")
            else:
                result = True

        except sqlite3.Error as e:
            self._logger.error(f"update_panel_group error: {e}")
        finally:
            conn.close()
        return result

    def get_panel_groups(self) -> list[dict]:
        groups: list[dict] = []
        try:
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row  # So we can access columns by name
            cursor = conn.cursor()

            query = """
                    SELECT id, name
                    FROM PanelsGroups
                    ORDER BY id
                    """

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                group = {
                    'id': row['id'],
                    'name': row['name']
                }
                groups.append(group)

        except sqlite3.Error as e:
            self._logger.error(
                f"ConfigStorage::get_panel_groups: SQLite error: {e}")
            return []
        finally:
            conn.close()
        return groups
