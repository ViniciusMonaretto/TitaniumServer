import importlib
from .protobuf_factory import ProtobufFactory

class GatewayProtobufFactory:
    @classmethod
    def create_protobuf_fact(cls, gateway_name, path) -> ProtobufFactory:
        protobuf_module = importlib.import_module(f".{gateway_name}_pb2", package=f".modules.titanium_mqtt.{path}")

        return ProtobufFactory(protobuf_module)