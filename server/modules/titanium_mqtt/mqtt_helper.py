from middleware.client_middleware import ClientMiddleware


class MqttHelper:
    @staticmethod
    def get_topic_from_mosquitto_obj_report(gateway, subtopic, indicator):
        return ClientMiddleware.get_status_topic(gateway, subtopic, indicator)

    @staticmethod
    def get_topic_from_mosquitto_obj_calibration(gateway, subtopic, indicator):
        return ClientMiddleware.get_calibrate_topic(gateway, subtopic, indicator)
