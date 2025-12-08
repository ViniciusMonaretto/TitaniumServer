import queue
import time
import uuid
import threading
import gc
from datetime import datetime, timedelta
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
import asyncio
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

# Default timeout for MongoDB operations (in seconds)
DEFAULT_MONGO_OPERATION_TIMEOUT = 600  # 10 minutes


class SensorDataStorage(ServiceInterface):
    """Service for storing and managing sensor data in MongoDB."""

    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self._middleware = middleware
        self._async_loop = AsyncioLoopThread()
        self._indexes_created = False
        self._gateway_status_subscribers: Dict[str, {
            'subscriber': StatuSubscribers, 'topics': []}] = {}
        self._last_status_by_sub_status_name: Dict[str, SensorInfo] = {}
        self._last_status_lock = threading.Lock()
        self._mongo_operation_timeout = DEFAULT_MONGO_OPERATION_TIMEOUT

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
                expireAfterSeconds=90 * 24 * 60 * 60,  # 60 days in seconds
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
                time.sleep(0.05)

            self._logger.debug(
                "SensorDataStorage: MongoDB connection established")
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage.initialize_system: MongoDB connection error {e}")

    def run_mongo_commands_async_background(self, coro, timeout: Optional[float] = None, timeout_callback: Optional[Callable] = None) -> Any:
        """
        Run MongoDB commands asynchronously in background with timeout protection.

        Each operation runs as an independent task, ensuring true parallelism.
        If one operation is stuck, others continue executing normally.

        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds (default: DEFAULT_MONGO_OPERATION_TIMEOUT)

        Returns:
            Future object representing the operation
        """
        if timeout is None:
            timeout = self._mongo_operation_timeout

        # Wrap coroutine with timeout protection
        async def coro_with_timeout():
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except asyncio.TimeoutError:
                self._logger.error(
                    f"SensorDataStorage:run_mongo_commands_async_background: "
                    f"Operation timed out after {timeout} seconds")
                if timeout_callback:
                    timeout_callback()
                raise
            except Exception as e:
                self._logger.error(
                    f"SensorDataStorage:run_mongo_commands_async_background: "
                    f"Error in MongoDB operation: {e}")
                raise

        # Schedule as independent task for true parallelism
        future = self._async_loop.run_coro(coro_with_timeout())
        future.add_done_callback(
            lambda f: f.exception() and
            self._logger.error(f"SensorDataStorage:run_mongo_commands_async_background:" +
                               f"Error running MongoDB command {f.exception()}"))
        return future

    def write_sensor_data_loop(self) -> None:
        """Main loop for writing sensor data to database."""
        # Calculate next minute boundary (e.g., if now is 10:00:30, next is 10:01:00)
        def get_next_minute_boundary():
            now = datetime.now()
            # Round up to next minute
            next_minute = (now.replace(
                second=0, microsecond=0) + timedelta(minutes=1))
            return next_minute

        # Wait until the next minute boundary
        next_minute = get_next_minute_boundary()
        wait_seconds = (next_minute - datetime.now()).total_seconds()
        if wait_seconds > 0:
            time.sleep(wait_seconds)

        while True:
            sensor_infos = []
            try:

                date_time_now = datetime.now().replace(
                    second=0, microsecond=0)
                with self._last_status_lock:

                    for sensor_topic in self._last_status_by_sub_status_name:
                        if date_time_now - self._last_status_by_sub_status_name[sensor_topic].timestamp > timedelta(minutes=1, seconds=30):
                            continue
                        sensor_infos.append(
                            {
                                "SensorFullTopic": sensor_topic,
                                "Timestamp": date_time_now,
                                "Value": self._last_status_by_sub_status_name[sensor_topic].value
                            }
                        )

                if sensor_infos:
                    self.add_info(sensor_infos)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self._logger.error(f"write_sensor_data_loop: {e}")

            next_minute = get_next_minute_boundary()
            wait_seconds = (next_minute - datetime.now()).total_seconds()
            if wait_seconds > 0:
                time.sleep(wait_seconds)

    def add_new_subscription(self, topic: str, gateway: str, indicator: str) -> tuple[bool, str]:
        """Add a new subscription for sensor data."""
        try:
            self.subscribe_to_status(gateway, topic, indicator)
            return True, ""

        except Exception as e:
            message = f"SensorDataStorage::add_new_subscription: Exception creating new table {e}"
            self._logger.error(message)
            return False, message

    def add_sensors_to_data_queue(self, status_info: Dict[str, Any]) -> None:
        """Add sensors data to the write queue."""
        try:
            for reading in status_info["data"].readings:
                self.add_sensor_data_to_queue(reading)
        except Exception as e:
            self._logger.error(
                f"SensorDataStorage::add_sensors_to_data_queue: Error adding data to queue {e}")

    def add_sensor_data_to_queue(self, status_info: Dict[str, Any]) -> None:
        """Add sensor data to the write queue."""
        try:
            # Store the last status sent for each subStatusName
            sub_status_name = status_info.full_topic

            with self._last_status_lock:
                self._last_status_by_sub_status_name[sub_status_name] = status_info
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
        gateway_topic = ClientMiddleware.get_gateway_status_topic(gateway)
        if gateway_topic not in self._gateway_status_subscribers:
            self._gateway_status_subscribers[gateway_topic] = {}
            self._gateway_status_subscribers[gateway_topic]['topics'] = []
            self._gateway_status_subscribers[gateway_topic]['subscriber'] = StatuSubscribers(
                self.add_sensors_to_data_queue, gateway_topic)
            self._middleware.add_subscribe_to_status(
                self._gateway_status_subscribers[gateway_topic]['subscriber'], gateway_topic)

        topic = ClientMiddleware.get_status_topic(
            gateway, status_name, indicator)
        self._gateway_status_subscribers[gateway_topic]['topics'].append(
            topic)

    def remove_subscription_from_status(self, gateway: str, status_name: str, indicator: str) -> None:
        """Remove subscription from status updates."""
        topic = ClientMiddleware.get_status_topic(
            gateway, status_name, indicator)
        gateway_topic = ClientMiddleware.from_status_topic_get_gateway_topic(
            topic)
        if gateway_topic not in self._gateway_status_subscribers:
            self._logger.error(
                f"SensorDataStorage::remove_subscription_from_status: Gateway topic {gateway_topic} not subscribed")
            return

        self._gateway_status_subscribers[gateway_topic]['topics'].remove(
            topic)
        if len(self._gateway_status_subscribers[gateway_topic]['topics']) == 0:
            self._middleware.remove_subscribe_from_status(
                self._gateway_status_subscribers[gateway_topic]['subscriber'], gateway_topic)
            del self._gateway_status_subscribers[gateway_topic]

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
            self._read_sensor_info(command,
                                   finish_callback),
            timeout_callback=lambda: self._middleware.send_command_answear(False, {"status": "error", "message": f"Ação excedeu o tempo de execução"}, command["requestId"]))

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
            query["Timestamp"]["$gt"] = dt

            if "endDate" in data:
                dt_end = datetime.strptime(
                    data["endDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
                query["Timestamp"]["$lt"] = dt_end

        data_out = {'info': {}}
        result = True

        try:
            # Adiciona limite e ordenação para controlar tamanho dos dados
            cursor = self._collection.find(query).sort(
                "Timestamp", -1)
            async for doc in cursor:
                sensor_name = doc["SensorFullTopic"]
                if sensor_name not in data_out['info']:
                    data_out['info'][sensor_name] = []
                tm = doc["Timestamp"]
                data_out["info"][sensor_name].append(
                    {'timestamp': tm.isoformat(), 'value': doc["Value"]})
            data_out['requestId'] = data['websocketId']
            await cursor.close()

        except Exception as e:
            self._logger.error(
                f"SensorDataStorage::read_sensor_info: Error trying to fetch info from table {e}")
            result = False

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
