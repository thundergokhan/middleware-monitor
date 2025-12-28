from abc import ABC, abstractmethod
import time
from src.utils.logger import get_logger

class BaseMonitor(ABC):
    """
    Abstract Base Class for all service monitors.
    Enforces a common interface for checking health.
    """

    def __init__(self, service_config):
        self.service_config = service_config
        self.name = service_config.get('name', 'Unknown Service')
        self.service_type = service_config.get('type', 'GENERIC')
        self.logger = get_logger(f"Monitor-{self.name}")

    @abstractmethod
    def check_health(self):
        """
        Performs the health check logic.
        
        Returns:
            dict: A dictionary containing:
                - status (bool): True if healthy, False otherwise.
                - response_time (float): Time taken in seconds.
                - message (str): Detailed status message or error.
                - timestamp (float): checking time.
        """
        pass

    def _generate_result(self, status, response_time, message):
        """
        Helper to construct the result dictionary.
        """
        return {
            "name": self.name,
            "type": self.service_type,
            "status": status,
            "response_time": round(response_time, 4),
            "message": message,
            "timestamp": time.time(),
            "config": self.service_config # Include config for reporting context
        }
