import importlib
import os

current_folder = os.path.dirname(os.path.abspath(__file__))

class DataConverter:
    def convert_data(self, status_name, obj):
        try:
            module = importlib.import_module(f".{status_name}", package="middleware.data_converter")
            cls = getattr(module, status_name.capitalize())
            instance = cls()
            return instance.convert_in_new_status(obj)
        except Exception as e:
            return None
