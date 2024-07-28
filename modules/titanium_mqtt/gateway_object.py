
class GatewayObject:
    _topics_map = {}

    def __init__(self, topics):
        for topic in topics:
            topicInfo = {}
            topicInfo["classStructure"] = topics["classStructure"]
            topicInfo["data"] = self.arrange_topic_data(topics["data"])
            self._topics_map[topic["id"]] = topicInfo

    def arrange_topic_data(self, topic_data):
        out_obj = {}
        for data in topic_data:
            out_obj[data["name"]] = data["type"]
        return out_obj
    
    def transform_json_obj(self, data, type):
        if(type == "string"):
            return str(data)
        if(type == "uInt"):
            return int(data)
        if(type == "int"):
            return int(data)
        return data
        
    def get_class_from_mqtt_message(self, mosquitto_id, mosquitto_json):
        if(mosquitto_id in self._topics_map):
            out_data = {}
            topic_info = self._topics_map[mosquitto_id]
            obj_name = topic_info["classStructure"]
            
            for name, value in mosquitto_json:
                topic_type = topic_info["data"][name]
                out_data[name] = self.transform_json_obj(value,topic_type)
            
            return {"name": obj_name, "data": out_data}
        else:
            print("id" + {mosquitto_id} + "not mapped")
        
        return None