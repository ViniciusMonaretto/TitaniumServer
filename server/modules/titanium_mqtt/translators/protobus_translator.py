from .translator_model import PayloadTranslator
from .protobus.protobus_parser import parser as ProtobusParser
import json
import base64

class ProtobusTranslator(PayloadTranslator):
    def initialize(self, subtopic, payload):
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        ProtobusParser.parse(f"{current_file_path}/titanium.proto", current_file_path)
    
    def translate_payload(self, subtopic, payload, gateway):
        memory_area = subtopic
        decoded_message = payload.decode('utf-8')
        json_data = json.loads(decoded_message)
    
        print(f"Received JSON: {json.dumps(json_data, indent=4)}")
        base64_raw_data = json_data["raw_data"]
        byte_stream = base64.b64decode(base64_raw_data)

        gateway_translator = self._gateways[gateway]

        protobuf = gateway_translator.create_instance(memory_area)

        return protobuf.ParseFromString(byte_stream)
    