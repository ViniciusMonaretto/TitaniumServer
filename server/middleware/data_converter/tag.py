
def convert_tag(self, data):
    mp = {0x3ffcee10: "João Silva"}

    if data["value"] in mp:
        return {"value": mp[data], "timestamp": data["timestamp"]}
    else:
        return data