class ProtobufFactory:

    def __init__(self, protobuf_module):
        self.module = protobuf_module
        self.memory_area_dict = {
            key: x.number for key, x in protobuf_module.MemoryAreas.DESCRIPTOR.values_by_name.items()
        }

    def create_instance(self, index: int):

        if index not in self.memory_area_dict.values():
            raise ValueError(
                f"Unsupported Memory Area! Valid options are: {list(self.memory_area_dict.values())}"
            )
        
        memory_areas_definitions = self.module.MemoryAreasDefinitions()
        descriptor_object = memory_areas_definitions.DESCRIPTOR
        
        for field in descriptor_object.fields:
            if field.number == index:
                return globals()[field.message_type.name]()
        
        return None