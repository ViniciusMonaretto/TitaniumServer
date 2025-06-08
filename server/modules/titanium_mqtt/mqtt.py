import threading
import queue
import paho.mqtt.client as mqtt

from support.logger import Logger

from .translators.direct_translator import DirectTranslator
from .translators.translator_model import PayloadTranslator
 

SUBSCRIBE_TOPIC_LIST = [("/titanium/#", 0)]

PUBLISH_TOPIC_LIST =   ["GetLevel", "titanium/level"]

GATEWAY_CONFIG_DIR = "titaniumGatewaysConfigs"

MQTT_SERVER = "mqtt.eclipseprojects.io"

MQTT_PORT = 1883

class TitaniumMqtt:
    world_count = 0
    world_count_rev = 0
    world_count2 = 0
    world_count2_rev = 0

    _client: mqtt.Client
    def __init__(self, middleware):
        self._logger = Logger()
        self._subscribe_topic_list = SUBSCRIBE_TOPIC_LIST
        self._publish_topics_list = PUBLISH_TOPIC_LIST

        self._end_thread = False

        self._gateways = {}
        self._middleware = middleware
        self._translator: PayloadTranslator = DirectTranslator()
        self._translator.initialize()

        self._read_queue = queue.Queue()

        self._messages_handler = threading.Thread(target=self.handle_incoming_messages, daemon=True)

    def on_connect(self, client, userdata, _flags, rc):
        self._logger.info(f"MqqtServer: Connected with result code {rc}")
        client.subscribe(userdata['subscribe_topics'])
            
    def on_message(self, _c, _u, msg):
        self._logger.debug(f"Received message: {msg.topic} {msg.payload}")
        self.world_count+=1
        # if(self.world_count == 40):
        #     #print(f"batch completed 1 " + str(self.world_count_rev))
        #     self.world_count_rev+=1
        #     if(self.world_count_rev==3):
        #         self.world_count_rev = 0
        #     self.world_count = 0
        self._read_queue.put(msg)

    def run(self):
        self.world_count = 0
        self.world_count2 = 0
        self._client = mqtt.Client()

        user_data = {}
        user_data['subscribe_topics'] = self._subscribe_topic_list 
        user_data['publish_topics'] = self._publish_topics_list
        self._client.user_data_set(user_data)

        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        try:

            self._client.connect(MQTT_SERVER, MQTT_PORT, 60)
            self._messages_handler.start()
            self._client.loop_start()
        except Exception as e:
            self._logger.error(f"Error Connecting to Mqtt: {e}")
    
    def execute(self, command):
        topic = self.get_topic_from_command(command.name)
        self._client.publish(topic, command.message)
    
    def handle_incoming_messages(self):
        while(not self._end_thread):
            try:
                msg = self._read_queue.get_nowait()

                msg_split = msg.topic.split('/')

                if not len(msg_split) == 5:
                    self._logger.error(f"TitaniumMqtt::on_message: mqtt topic {msg.topic} not valid")
                else:
                    msg_id = str(msg_split[2])
                    cls = self._translator.translate_payload(msg_split[3], msg.payload, msg_id)

                    self._logger.debug(f"Received message: {msg.topic} {cls}")

                    topic_name = TitaniumMqtt.get_topic_from_mosquitto_obj(msg_id, cls)
                    self.world_count2 += 1

                    self._middleware.send_status(topic_name, {'data': cls['data'], 'timestamp':cls['timestamp']})
            except queue.Empty:
                pass
            except Exception as e:
                self._logger.error(f"Mqtt.handle_incoming_messages: Error Parsing messages {e}")
        
        
    
    def stop(self):
        self._end_thread = True
        self._client.loop_stop()
        self._client.disconnect()
        self._messages_handler.join()

    def get_topic_from_command(self, command):
        if command in  self._publish_topics_list:
            return self._publish_topics_list[command]
        return command

    @staticmethod
    def get_topic_from_mosquitto_obj(mosquitto_id, cls):
        return mosquitto_id + '/' + cls['name']
