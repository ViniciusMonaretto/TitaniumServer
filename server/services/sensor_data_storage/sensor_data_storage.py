from datetime import datetime
import queue
from typing import Union
import uuid

import pytz
from middleware.middleware import ClientMiddleware
from dataModules.sensor_info import SensorInfo
from middleware.status_subscriber import StatuSubscribers
from services.sensor_data_storage.async_loop_thread import AsyncioLoopThread
from services.sensor_data_storage.sensor_data_storage_commands import SensorDataStorageCommands
from services.service_interface import ServiceInterface
from support.logger import Logger
from pymongo import ASCENDING  # Needed for specifying index order

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import threading


MONGO_DB_URI = "mongodb://root:example@localhost:27017/"
MONGO_DB_NAME = "IoCloud"
MONGO_DB_COLLECTION = "SensorData"

class SensorDataStorage(ServiceInterface):
    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self._middleware = middleware

        self.initialize_commands()
        self.initialize_system()
        self.id = str(uuid.uuid4())
        self._subscriptions_add = 0

        self._async_loop = AsyncioLoopThread()

        self._info_wrything_thread = threading.Thread(target=self.write_sensor_data_loop, daemon=True)
        self._info_wrything_thread.start()

        self._status_subscribers = {}

        self._logger.info("SensorDataStorage initialized")

    def initialize_commands(self):
        commands = {
            SensorDataStorageCommands.ADD_SENSOR_INFO: self.add_sensor_info_command,
            SensorDataStorageCommands.READ_SENSOR_INFO: self.read_sensor_info_command,
            SensorDataStorageCommands.ERASE_SENSOR_INFO: self.erase_sensor_info_command
            }
        self._middleware.add_commands(commands)

    async def create_indexes_of_db(self): 
        self._collection.create_index(
                    [("SensorFullTopic", ASCENDING), ("Timestamp", ASCENDING)],
                    background=True
                )


    def initialize_system(self):
        try:
            self._client = AsyncIOMotorClient(MONGO_DB_URI)

            self._write_queue = queue.Queue()

            self._db = self._client[MONGO_DB_NAME]
            self._collection = self._db[MONGO_DB_COLLECTION]
            

            asyncio.get_event_loop().run_until_complete( lambda :
                
            )

            self._logger.debug("SensorDataStorage: MongoDB connection established")
        except Exception as e:
            self._logger.error(f"SensorDataStorage.initialize_system: MongoDB connection error {e}")

    def run_mongo_commands_async_background(self, coro):
        future = self._async_loop.run_coro(coro)

        return future

    def write_sensor_data_loop(self):
        while True:
            sensor_infos = []
            while not self._write_queue.empty():
                try:
                    sensor_info: SensorInfo = self._write_queue.get(timeout=1)
                    sensor_info._timestamp = datetime.fromisoformat(sensor_info._timestamp)
                    
                    sensor_infos.append(sensor_info.to_json())
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self._logger.error(f"SensorDataStorage::write_sensor_data_loop: Error getting data from write queue {e}")
                    break
            
            if len(sensor_infos) > 0:
                self.add_info(sensor_infos)
            threading.Event().wait(1)


    def add_new_subscription(self, topic: str, gateway: str) ->  Union[bool, str]:
        try:
            self.subscribe_to_status(gateway, topic)
            return True, ""
        
        except Exception as e:
            message = f"SensorDataStorage::add_new_subscription: Exceptio creating new table {e}"
            self._logger.error(message)
            return False, message
    
    def get_panel_topic(self, gateway, status_name):
        return gateway + "/" + status_name

    def add_sensor_data_to_queue(self, status_info):
        try:
            self._write_queue.put(SensorInfo(status_info["subStatusName"].replace('/', '-'),
                                             datetime.fromisoformat(status_info["data"]["timestamp"]),
                                             status_info["data"]["data"]))
        except Exception as e:
            self._logger.error(f"SensorDataStorage::add_sensor_data_to_queue: Error adding data to queue {e}")
    
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

    

    def add_sensor_info_command(self, command):
        data_info = command["data"]
        self.add_info(data_info, lambda result: self._middleware.send_command_answear( result, "", command["requestId"]))
    
    def add_info(self, data: object, finishCallback = None):
        self.run_mongo_commands_async_background(self._add_info(data, finishCallback))

    async def _add_info(self, data, finishCallback = None):
        try:
            if isinstance(data, list):
                result = await self._collection.insert_many(data)
                self._logger.debug(f"SensorDataStorage:add_info: Inserted documents count: {len(result.inserted_ids)}")
            else:
                result = await self._collection.insert_one(data)
                print(f"SensorDataStorage:add_info: Inserted documents ID: {result.inserted_id}")
        except Exception as e:
            self._logger.error(f"SensorDataStorage:add_info: error adding info {e}")
        if finishCallback:
            finishCallback(result)
    
    def read_sensor_info_command(self, command):
        self.read_sensor_info(command, lambda result, data_out: self._middleware.send_command_answear( result, data_out, command["requestId"]))
    
    def read_sensor_info(self, command: object, finishCallback):
        self.run_mongo_commands_async_background(self._read_sensor_info(command, finishCallback))

    async def _read_sensor_info(self, command: object, finishCallback):
        data = command["data"]

        sensor_infos = data["sensorInfos"]

        query = {
                "SensorFullTopic": {"$in": []}
            }

        for index, info in enumerate(sensor_infos):
            table_name = info["topic"]
            gateway = info["gateway"]
            if(gateway):
                table_name = gateway + '-' + table_name
            
            query["SensorFullTopic"]["$in"] = query["SensorFullTopic"]["$in"] + [table_name]
        
        if("beginDate" in data):
            dt = datetime.strptime( data["beginDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
            query["Timestamp"] = {}
            query["Timestamp"]["$gt"] = dt.timestamp()

            if("endDate" in data):
                dt_end = datetime.strptime( data["endDate"][:26], '%Y-%m-%dT%H:%M:%S.%f')
                query["Timestamp"]["$gt"] = dt_end.timestamp()

        data_out = {'info': {}}

        result = True

        try:
            cursor = self._collection.find(query)
            local_tz = pytz.timezone("America/Sao_Paulo")
            async for doc in cursor:
                sensor_name = doc["SensorFullTopic"]
                if sensor_name not in data_out['info']:
                    data_out['info'][sensor_name] = []
                tm = datetime.fromtimestamp(doc["Timestamp"], local_tz)
                data_out["info"][sensor_name].append({'timestamp': tm.isoformat(), 'value': doc["Value"]})
            data_out['requestId'] = data['websocketId']
            
        except Exception as e:
            self._logger.error(f"SensorDataStorage::read_sensor_info: Error trying to fetch info from table {e}")
            result = False

        finishCallback(result, data_out)
    
    def erase_sensor_info_command(self, commands):
        raise NotImplementedError()