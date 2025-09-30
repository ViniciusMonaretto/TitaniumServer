import logging
import threading
from logging.handlers import RotatingFileHandler


class SingletonMeta(type):
    """ Thread-safe Singleton Metaclass """
    _instances = {}
    _lock = threading.Lock()  # Lock to synchronize threads

    def __call__(cls, *args, **kwargs):
        with cls._lock:  # Ensure only one instance is created
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    def __init__(self, log_file="app.log", level=logging.INFO, max_size=5*1024*1024, backup_count=3):
        self.logger = logging.getLogger("TitaniumLogger")
        self.logger.setLevel(level)
        self.logger.propagate = False

        if not self.logger.hasHandlers():
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s")

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # Rotating File Handler - keeps 4 total logs (1 main + 3 backups)
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_size, backupCount=backup_count)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
