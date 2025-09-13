import queue
import uuid
import threading
import gc
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import sys
import os
from support.logger import Logger
from services.service_interface import ServiceInterface
from services.sensor_data_storage.sensor_data_storage_commands import SensorDataStorageCommands
from services.sensor_data_storage.async_loop_thread import AsyncioLoopThread
from middleware.status_subscriber import StatuSubscribers
from dataModules.sensor_info import SensorInfo
from middleware.client_middleware import ClientMiddleware


# Third-party imports
import pytz
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

# Local application imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Get MongoDB connection details from environment variables
MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', '27017')
MONGO_USER = os.getenv('MONGO_USER', 'root')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'example')
MONGO_DB_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
MONGO_DB_NAME = "IoCloud"
MONGO_DB_COLLECTION = "SensorData"


class SensorDataStorage(ServiceInterface):
    """Service for storing and managing sensor data in MongoDB."""

    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self._middleware = middleware
        self._async_loop = AsyncioLoopThread()
        self._indexes_created = False
        self._status_subscribers: Dict[str, StatuSubscribers] = {}
        self._last_status_by_sub_status_name: Dict[str, Dict[str, Any]] = {}
        self._last_status_lock = threading.Lock()

        self.initialize_commands()
        self.initialize_system()
        self.id = str(uuid.uuid4())

        self._info_writing_thread = threading.Thread(
            target=self.write_sensor_data_loop, daemon=True)
        self._info_writing_thread.start()

        self._logger.info("SensorDataStorage initialized")

    def initialize_commands(self) -> None:
        """Initialize command handlers."""
        commands = {
            SensorDataStorageCommands.ADD_SENSOR_INFO: self.add_sensor_info_command,
            SensorDataStorageCommands.READ_SENSOR_INFO: self.read_sensor_info_command,
            SensorDataStorageCommands.ERASE_SENSOR_INFO: self.erase_sensor_info_command
        }
        self._middleware.add_commands(commands)

    async def create_indexes_of_db(self) -> None:
        """Create database indexes for efficient queries and TTL."""
        if not self._indexes_created:
            # Create compound index for efficient queries
            await self._collection.create_index(
                [("SensorFullTopic", ASCENDING), ("Timestamp", ASCENDING)],
                background=True
            )

            # Create TTL index to expire documents after 60 days
            await self._collection.create_index(
                "Timestamp",
                expireAfterSeconds=60 * 24 * 60 * 60,  # 60 days in seconds
                background=True
            )

            self._indexes_created = True

    def initialize_system(self) -> None:
        """Initialize MongoDB connection and create indexes."""
        try:
            self._client = AsyncIOMotorClient(MONGO_DB_URI)
            self._write_queue = queue.Queue()
            self._db = self._client[MONGO_DB_NAME]
            self._collection = self._db[MONGO_DB_COLLECTION]

            self.run_mongo_commands_async_background(
                self.create_indexes_of_db())

            while not self._indexes_created:
                pass

            self._logger.debug(
                "SensorDataStorage: MongoDB connection established")
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage.initialize_system: MongoDB connection error {e}")

    def run_mongo_commands_async_background(self, coro) -> Any:
        """Run MongoDB commands asynchronously in background."""
        future = self._async_loop.run_coro(coro)
        return future

    def write_sensor_data_loop(self) -> None:
        """Main loop for writing sensor data to database."""
        while True:
            sensor_infos = []
            while not self._write_queue.empty():
                try:
                    sensor_info: SensorInfo = self._write_queue.get(timeout=1)
                    # Convert timestamp to string if it's not already a string
                    if isinstance(sensor_info.timestamp, str):
                        sensor_info.timestamp = datetime.fromisoformat(
                            sensor_info.timestamp)
                    # If it's already a datetime object, use it directly
                    # (no need to reassign)

                    sensor_infos.append(sensor_info.to_json())
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._logger.error(
                        f"SensorDataStorage::write_sensor_data_loop: Error getting data from write queue {e}")
                    break

            if sensor_infos:
                self.add_info(sensor_infos)
            threading.Event().wait(1)

    def add_new_subscription(self, topic: str, gateway: str, indicator: str) -> tuple[bool, str]:
        """Add a new subscription for sensor data."""
        try:
            self.subscribe_to_status(gateway, topic, indicator)
            return True, ""

        except Exception as e:
            message = f"SensorDataStorage::add_new_subscription: Exception creating new table {e}"
            self._logger.error(message)
            return False, message

    def add_sensor_data_to_queue(self, status_info: Dict[str, Any]) -> None:
        """Add sensor data to the write queue."""
        try:
            # Store the last status sent for each subStatusName
            sub_status_name = status_info["subStatusName"]
            with self._last_status_lock:
                self._last_status_by_sub_status_name[sub_status_name] = status_info["data"]

            self._write_queue.put(SensorInfo(sub_status_name,
                                             status_info["data"].timestamp,
                                             status_info["data"].value))
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage::add_sensor_data_to_queue: Error adding data to queue {e}")

    def get_last_status_for_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get the last status sent for a specific topic in a thread-safe manner."""
        with self._last_status_lock:
            return self._last_status_by_sub_status_name.get(topic)

    def get_all_last_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get all last statuses for all topics in a thread-safe manner."""
        with self._last_status_lock:
            return self._last_status_by_sub_status_name.copy()

    def subscribe_to_status(self, gateway: str, status_name: str, indicator: str) -> None:
        """Subscribe to status updates for a specific sensor."""
        topic = ClientMiddleware.get_status_topic(
            gateway, status_name, indicator)
        if topic not in self._status_subscribers:
            self._status_subscribers[topic] = StatuSubscribers(
                self.add_sensor_data_to_queue, topic)
            self._middleware.add_subscribe_to_status(
                self._status_subscribers[topic], topic)

    def remove_subscription_from_status(self, gateway: str, status_name: str, indicator: str) -> None:
        """Remove subscription from status updates."""
        topic = ClientMiddleware.get_status_topic(
            gateway, status_name, indicator)
        if topic in self._status_subscribers:
            self._middleware.remove_subscribe_from_status(
                self._status_subscribers[topic], topic)
            del self._status_subscribers[topic]

    def add_sensor_info_command(self, command: Dict[str, Any]) -> None:
        """Handle add sensor info command."""
        data_info = command["data"]
        self.add_info(data_info, lambda result: self._middleware.send_command_answear(
            result, "", command["requestId"]))

    def add_info(self, data: Any, finish_callback: Optional[Callable] = None) -> None:
        """Add sensor info to database."""
        self.run_mongo_commands_async_background(
            self._add_info(data, finish_callback))

    async def _add_info(self, data: Any, finish_callback: Optional[Callable] = None) -> None:
        """Add sensor info to database asynchronously."""
        result = None
        try:
            if isinstance(data, list):
                result = await self._collection.insert_many(data)
                self._logger.debug(
                    f"SensorDataStorage:add_info: Inserted documents count: {len(result.inserted_ids)}")
            else:
                result = await self._collection.insert_one(data)
                self._logger.debug(
                    f"SensorDataStorage:add_info: Inserted documents ID: {result.inserted_id}")
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage:add_info: error adding info {e}")
        if finish_callback:
            finish_callback(result)

    def read_sensor_info_command(self, command: Dict[str, Any]) -> None:
        """Handle read sensor info command."""
        self.read_sensor_info(command, lambda result, data_out: self._middleware.send_command_answear(
            result, data_out, command["requestId"]))

    def read_sensor_info(self, command: Dict[str, Any], finish_callback: Callable) -> None:
        """Read sensor info from database."""
        self.run_mongo_commands_async_background(
            self._read_sensor_info(command, finish_callback))

    async def _read_sensor_info(self, command: Dict[str, Any], finish_callback: Callable) -> None:
        """Read sensor info from database asynchronously."""
        data = command["data"]
        sensor_infos = data["sensorInfos"]

        query: Dict[str, Any] = {
            "SensorFullTopic": {"$in": []}
        }

        for info in sensor_infos:
            table_name = info["topic"]
            gateway = info["gateway"]
            indicator = info["indicator"]
            table_name = ClientMiddleware.get_status_topic(
                gateway, table_name, indicator)

            query["SensorFullTopic"]["$in"].append(table_name)

        if "beginDate" in data:
            dt = datetime.strptime(
                data["beginDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
            query["Timestamp"] = {}
            query["Timestamp"]["$gt"] = dt.timestamp()

            if "endDate" in data:
                dt_end = datetime.strptime(
                    data["endDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
                query["Timestamp"]["$lt"] = dt_end.timestamp()

        data_out = {'info': {}}
        result = True

        try:
            # Adiciona limite e ordenação para controlar tamanho dos dados
            cursor = self._collection.find(query).sort(
                "Timestamp", -1)
            local_tz = pytz.timezone("America/Sao_Paulo")
            async for doc in cursor:
                sensor_name = doc["SensorFullTopic"]
                if sensor_name not in data_out['info']:
                    data_out['info'][sensor_name] = []
                tm = datetime.fromtimestamp(doc["Timestamp"], local_tz)
                data_out["info"][sensor_name].append(
                    {'timestamp': tm.isoformat(), 'value': doc["Value"]})
            data_out['requestId'] = data['websocketId']

        except Exception as e:
            self._logger.error(
                f"SensorDataStorage::read_sensor_info: Error trying to fetch info from table {e}")
            result = False
        finally:
            # Garbage collection final para liberar memória
            gc.collect()

        data_out["commandId"] = command["requestId"]
        finish_callback(result, data_out)

    def erase_sensor_info_command(self, command: Dict[str, Any]) -> None:
        """Handle erase sensor info command."""
        data = command["data"]
        sensor_infos = data["sensorInfos"]

        sensors_ids = []
        for info in sensor_infos:
            table_name = info["topic"]
            gateway = info["gateway"]
            indicator = info["indicator"]
            table_name = ClientMiddleware.get_status_topic(
                gateway, table_name, indicator)

            sensors_ids.append(table_name)

        dt_begin = None
        dt_end = None

        if "beginDate" in data:
            dt_begin = datetime.strptime(
                data["beginDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')

            if "endDate" in data:
                dt_end = datetime.strptime(
                    data["endDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')

        self.erase_sensor_info(sensors_ids,
                               dt_begin,
                               dt_end,
                               lambda result, data_out: self._middleware.send_command_answear(result, data_out, command["requestId"]))

    def erase_sensor_info(self,
                          sensors_ids: List[str],
                          begin_date: Optional[datetime],
                          end_date: Optional[datetime],
                          finish_callback: Callable) -> None:
        """Erase sensor info from database."""
        self.run_mongo_commands_async_background(self._erase_sensor_info(sensors_ids,
                                                                         begin_date,
                                                                         end_date,
                                                                         finish_callback))

    async def _erase_sensor_info(self,
                                 sensors_ids: List[str],
                                 begin_date: Optional[datetime],
                                 end_date: Optional[datetime],
                                 finish_callback: Callable) -> None:
        """Erase sensor info from database asynchronously."""

        result = False
        message = "Successo"

        query: Dict[str, Any] = {
            "SensorFullTopic": {"$in": sensors_ids}
        }

        if begin_date:
            query["Timestamp"] = {}
            query["Timestamp"]["$gt"] = begin_date.timestamp()

        if end_date:
            if "Timestamp" not in query:
                query["Timestamp"] = {}
            query["Timestamp"]["$lt"] = end_date.timestamp()

        try:
            result = await self._collection.delete_many(query)
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage::erase_sensor_info: Error trying to fetch info from table {e}")
            message = "Erro removendo ids do banco"
            result = False

        finish_callback(result, message)
