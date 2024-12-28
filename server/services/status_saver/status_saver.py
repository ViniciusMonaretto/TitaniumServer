import sqlite3
import json
import os
from datetime import datetime
from middleware.status_subscriber import StatuSubscribers
from middleware.middleware import ClientMiddleware
import uuid

DB_CONFIG = "db_status_saves.json"
DB_NAME = "status_saver.db"

class SatatusSaver:
    def __init__(self, middleware: ClientMiddleware):
        self.id = str(uuid.uuid4())
        self._subscriptions_add = 0
        self._status_subscribers = {}
        self._middleware = middleware

        self.initialize_data_bank()
        
    def get_panel_topic(self, gateway, status_name):
        return gateway + "/" + status_name

    def initialize_data_bank(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        script_directory = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_directory, DB_CONFIG)
            
        with open(filename, 'r') as json_file:
            try:
                data = json.load(json_file) 
                
                for configs in data["dbCOnfig"]:
                    cursor.execute(configs["tableConfig"]) 
                    self.subscribe_to_status(configs["gateway"], configs["topic"]) 

                conn.commit()
                conn.close()
            except json.JSONDecodeError as e:
                print(f"Error processing file {filename}: {e}")
    
    def subscribe_to_status(self, gateway, status_name):
        topic = self.get_panel_topic(gateway, status_name)
        self._status_subscribers[topic] = StatuSubscribers(self.send_status, topic, self.id + str(self._subscriptions_add))
        self._middleware.add_subscribe_to_status(self._status_subscribers[topic], topic)
        self._subscriptions_add+=1