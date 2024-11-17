import paho.mqtt.client as mqtt
import os
import json
import time
import base64
from .gateway_object import GatewayObject
from .gateway_protobuf_factory import GatewayProtobufFactory
from .protobus_parser import parser as ProtobusParser

SUBSCRIBE_TOPIC_LIST = [("titanium_area/#", 0)]

PUBLISH_TOPIC_LIST =   ["GetLevel", "titanium/level"]

GATEWAY_CONFIG_DIR = "titaniumGatewaysConfigs"


class TitaniumMqtt:
    def __init__(self, middleware):
        self._subscribe_topic_list = SUBSCRIBE_TOPIC_LIST
        self._publish_topics_list = PUBLISH_TOPIC_LIST

        self._gateways = {}

        self._middleware = middleware

        self.register_gateways()

        current_file_path = os.path.dirname(os.path.abspath(__file__))

        ProtobusParser.parse(f"{current_file_path}/titanium.proto", current_file_path)

    def register_gateways(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        json_directory = os.path.join(script_directory, GATEWAY_CONFIG_DIR)
        for filename in os.listdir(json_directory):
            if filename.endswith('_pb2.py'):  # Check if the file is a valid profibuf file
                gateway = filename.removesuffix("_pb2.py")
                self._gateways[gateway] = GatewayProtobufFactory.create_protobuf_fact(gateway, GATEWAY_CONFIG_DIR)

#######
    # def register_gateways(self):
    #     script_directory = os.path.dirname(os.path.abspath(__file__))
    #     json_directory = os.path.join(script_directory, GATEWAY_CONFIG_DIR)
    #     for filename in os.listdir(json_directory):
    #         if filename.endswith('.json'):  # Check if the file is a JSON file
    #             # Construct the full path to the file
    #             file_path = os.path.join(json_directory, filename)

    #             # Open the JSON file and load its content
    #             with open(file_path, 'r') as json_file:
    #                 try:
    #                     data = json.load(json_file)  # Load the JSON data
    #                     # Process the JSON data (replace this with your logic)
    #                     self._gateways[data["firmware"]["name"]] = GatewayObject(data["firmware"]["memory_areas"])

    #                     print(f"Processing file: {filename}")
    #                 except json.JSONDecodeError as e:
    #                     print(f"Error processing file {filename}: {e}")

    def on_connect(self, client, userdata, flags, rc):
        print(f"MqqtServer: Connected with result code {rc}")
        client.subscribe(userdata['subscribe_topics'])
            
    def on_message(self, client, userdata, msg):
        decoded_msg = msg.payload.decode()
        msg_split = msg.topic.split('/')

        if not len(msg_split) < 2:
            print(f"TitaniumMqtt::on_message: mqtt topic {msg.topic} not valid")
            return

        id = msg_split[0]
        if not id in self._gateways:
            print("TitaniumMqtt::on_message: gateway id not registered")
            return
        cls = self.get_class_from_mqtt_message(msg, id)

        print(f"Received message: {msg.topic} {cls}")

        topic_name = TitaniumMqtt.get_topic_from_mosquitto_obj(msg_split[1], cls)
        self._middleware.send_status(topic_name, cls['data'])

    def run(self):
        self.client = mqtt.Client()

        user_data = {}
        user_data['subscribe_topics'] = self._subscribe_topic_list 
        user_data['publish_topics'] = self._publish_topics_list
        self.client.user_data_set(user_data)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("mqtt.eclipseprojects.io", 1883, 60)
        self.client.loop_start()

    def get_class_from_mqtt_message(self, message, gateway):
        memory_area = int(message.topic.split("/")[-1])
        decoded_message = message.payload.decode('utf-8')
        json_data = json.loads(decoded_message)
    
        print(f"Received JSON: {json.dumps(json_data, indent=4)}")
        base64_raw_data = json_data["raw_data"]
        byte_stream = base64.b64decode(base64_raw_data)

        gateway_translator = self._gateways[gateway]

        protobuf = gateway_translator.create_instance(memory_area)

        return protobuf.ParseFromString(byte_stream)
    
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