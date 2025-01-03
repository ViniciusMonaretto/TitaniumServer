from abc import ABC, abstractmethod
from collections.abc import Callable

class ServiceInterface(ABC):
    _command_list: dict[str, Callable[[dict], None]] = {}

    def get_command_list(self):
        return self._command_list
    
    @abstractmethod
    def initialize_commands(self):
        pass