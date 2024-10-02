class DataConverter:

    def convert_data(self, status_name, object):
        method_to_call = getattr(self, status_name, None)
        if method_to_call and callable(method_to_call):
            return method_to_call(object)
        return object
