import json

class ServerDataInput:
    id = ""
    value = 0

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __init__(self, jsonObj:dict):
        self.id = jsonObj["id"]
        self.value = jsonObj["value"]
