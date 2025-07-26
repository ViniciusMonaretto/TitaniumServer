
class Tag:
    def convert_in_new_status(self, data):
        mp = {0x3ffcee10: "João Silva"}
        if data["value"] in mp:
            return {"value": mp[data["value"]], "timestamp": data["timestamp"]}
        else:
            return data
