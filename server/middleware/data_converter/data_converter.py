import importlib.util
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

def convert_tag(data):
    mp = {1073539744: "João Silva"}

    if data in mp:
        return mp[data]
    else:
        return data

class DataConverter:

    def convert_data(self, status_name, object):
        """try:
            cls = getattr( status_name)
            if isinstance(cls, type):
                instance = globals()[status_name]()
                return instance.convert(object)
        except:
            pass"""
        if status_name == 'tag_uuid':
            return convert_tag(object)
        return object
