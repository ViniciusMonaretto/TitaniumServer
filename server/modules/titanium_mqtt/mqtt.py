import threading
import queue
import paho.mqtt.client as mqtt

from modules.titanium_mqtt.translators.io_cloud_api import IoCloudApiTranslator
from modules.titanium_mqtt.translators.payload_model import MqttPayloadModel
from middleware.client_middleware import ClientMiddleware
from modules.titanium_mqtt.mqtt_commands import MqttCommands
from support.logger import Logger

from .translators.translator_model import PayloadTranslator
 

SUBSCRIBE_TOPIC_LIST = [("iocloud/#", 0)]

PUBLISH_TOPIC_LIST =   ["GetLevel", "titanium/level"]

GATEWAY_CONFIG_DIR = "titaniumGatewaysConfigs"

MQTT_SERVER = "mqtt.eclipseprojects.io"

MQTT_PORT = 1883

class TitaniumMqtt:
    _client: mqtt.Client
    def __init__(self, middleware: ClientMiddleware):
        self._logger = Logger()
        self._subscribe_topic_list = SUBSCRIBE_TOPIC_LIST
        self._publish_topics_list = PUBLISH_TOPIC_LIST

        self._end_thread = False

        self._gateways = {}
        self._middleware = middleware
        self._translator: PayloadTranslator = IoCloudApiTranslator()
        self._translator.initialize()

        self._read_queue = queue.Queue()

        self._command_handler = threading.Thread(target=self.handle_incoming_messages, daemon=True)
        self._messages_handler = threading.Thread(target=self.handle_incoming_messages, daemon=True)

    def initialize_commands(self):
        commands = {
            MqttCommands.CALIBRATION: self.calibrate_command
            }
        self._middleware.add_commands(commands)

    def calibrate_command(self, command):
        if(not self._client or not self._client.is_connected()):
           self._middleware.send_command_answear( False, "calibrate_command: Mqtt not connected", 
                                                  command["requestId"])
        topic = f"ioCloud/{command.gateway}/request/{command.sensor_type}/{command.sensor_indicator}"
        payload = {
            "action": "start",
            "offset": command.offset,
            "gain": command.gain
        }
        self._client.publish(topic, payload)
        self._middleware.send_command_answear( True, "sucess", command["requestId"])

    def on_connect(self, client, userdata, _flags, rc):
        self._logger.info(f"MqqtServer: Connected with result code {rc}")
        client.subscribe(userdata['subscribe_topics'])
            
    def on_message(self, _c, _u, msg):
        self._logger.debug(f"Received message: {msg.topic} {msg.payload}")
        self._read_queue.put(msg)

    def run(self):
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
                mqtt_message = self._translator.translate_incoming_message(msg.topic, msg.payload)

                if (mqtt_message):
                    topic_name = TitaniumMqtt.get_topic_from_mosquitto_obj(mqtt_message)
                    self._middleware.send_status(topic_name, mqtt_message.payload)
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
    def get_topic_from_mosquitto_obj(mqtt_message: MqttPayloadModel):
        if mqtt_message.action is "calibrateresponse":
            return ClientMiddleware.get_calibrate_topic( mqtt_message.gateway, mqtt_message.subtopic, mqtt_message.indicator)
        elif mqtt_message.action is "status":
            return ClientMiddleware.get_status_topic( mqtt_message.gateway, mqtt_message.subtopic, mqtt_message.indicator)
        else:
            Logger().warning(f"TitaniumMqtt::get_topic_from_mosquitto_obj: Mqtt message action not supported: {mqtt_message.action}")
