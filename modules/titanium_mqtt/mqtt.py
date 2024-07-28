import paho.mqtt.client as mqtt

SUBSCRIBE_TOPIC_LIST = [("titanium_area/#", 0)]

PUBLISH_TOPIC_LIST =   ["GetLevel", "titanium/level"]


class TitaniumMqtt:
    def __init__(self, middleware):
        self._subscribe_topic_list = SUBSCRIBE_TOPIC_LIST
        self._publish_topics_list = PUBLISH_TOPIC_LIST
        self._middleware = middleware

    def on_connect(self, client, userdata, flags, rc):
        print(f"MqqtServer: Connected with result code {rc}")
        client.subscribe(userdata['subscribe_topics'])

    def on_message(self, client, userdata, msg):
        print(f"Received message: {msg.topic} {msg.payload.decode()}")

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
