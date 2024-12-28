from .translator_model import PayloadTranslator
import json

class DirectTranslator(PayloadTranslator):
    def translate_payload(self, subtopic, payload, gateway):
        decoded_message = payload.decode('utf-8')
        json_data = json.loads(decoded_message)
        return {"name": subtopic, "data": json_data["value"], "timestamp": json_data["timestamp"]}