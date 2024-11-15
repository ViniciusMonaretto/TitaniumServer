class SubscriberInterface:
    _id = -1
    _topic = ""
    def send_status(self, status_data):
        pass

    def get_id(self):
        pass

    def get_topic(self):
        pass