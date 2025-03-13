import paho.mqtt.client as mqtt
import os
import json

from .gateway_object import GatewayObject
from .translators.protobus.gateway_protobuf_factory import GatewayProtobufFactory
from .translators.direct_translator import DirectTranslator
from .translators.translator_model import PayloadTranslator


SUBSCRIBE_TOPIC_LIST = [("/titanium/#", 0)]

PUBLISH_TOPIC_LIST =   ["GetLevel", "titanium/level"]

GATEWAY_CONFIG_DIR = "titaniumGatewaysConfigs"

MQTT_SERVER = "mqtt.eclipseprojects.io"

MQTT_PORT = 1883


class TitaniumMqtt:
    def __init__(self, middleware):
        self._subscribe_topic_list = SUBSCRIBE_TOPIC_LIST
        self._publish_topics_list = PUBLISH_TOPIC_LIST

        self._gateways = {}

        self._middleware = middleware

        self._translator: PayloadTranslator = DirectTranslator()

        self._translator.initialize()

   # def register_gateways(self):
   #     script_directory = os.path.dirname(os.path.abspath(__file__))
   #     json_directory = os.path.join(script_directory, GATEWAY_CONFIG_DIR)
   #     for filename in os.listdir(json_directory):
   #         if filename.endswith('_pb2.py'):  # Check if the file is a valid profibuf file
   #             gateway = filename.removesuffix("_pb2.py")
   #             self._gateways[gateway] = GatewayProtobufFactory.create_protobuf_fact(gateway, GATEWAY_CONFIG_DIR)

#######
    def register_gateways(self):
         script_directory = os.path.dirname(os.path.abspath(__file__))
         json_directory = os.path.join(script_directory, GATEWAY_CONFIG_DIR)
         for filename in os.listdir(json_directory):
             if filename.endswith('.json'):  # Check if the file is a JSON file
                # Construct the full path to the file
                file_path = os.path.join(json_directory, filename)

                # Open the JSON file and load its content
                with open(file_path, 'r') as json_file:
                    try:
                        data = json.load(json_file)  # Load the JSON data
                        # Process the JSON data (replace this with your logic)
                        self._gateways[data["firmware"]["name"]] = GatewayObject(data["firmware"]["memory_areas"])

                        print(f"Processing file: {filename}")
                    except json.JSONDecodeError as e:
                        print(f"Error processing file {filename}: {e}")

    def on_connect(self, client, userdata, flags, rc):
        print(f"MqqtServer: Connected with result code {rc}")
        client.subscribe(userdata['subscribe_topics'])
            
    def on_message(self, client, userdata, msg):
        msg_split = msg.topic.split('/')

        if not len(msg_split) == 5:
            print(f"TitaniumMqtt::on_message: mqtt topic {msg.topic} not valid")
            return

        id = str(msg_split[2])
        #if not id in self._gateways:
        #    print("TitaniumMqtt::on_message: gateway id not registered")
        #    return
        cls = self._translator.translate_payload(msg_split[3], msg.payload, id)

        print(f"Received message: {msg.topic} {cls}")

        topic_name = TitaniumMqtt.get_topic_from_mosquitto_obj(id, cls)
        self._middleware.send_status(topic_name, cls['data'])

    def run(self):
        self.client = mqtt.Client()

        user_data = {}
        user_data['subscribe_topics'] = self._subscribe_topic_list 
        user_data['publish_topics'] = self._publish_topics_list
        self.client.user_data_set(user_data)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:

            self.client.connect(MQTT_SERVER, MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error Connecting to Mqtt: {e}")
    
    def execute(self, command):
        topic = self.get_topic_from_command(command.name)
        self.client.publish(topic, command.message)
    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def get_topic_from_command(self, command):
        if command in  self._publish_topics_list:
            return self._publish_topics_list["command"]
        return command

    @staticmethod
    def get_topic_from_mosquitto_obj(mosquitto_id, cls):
        return mosquitto_id + '/' + cls['name']