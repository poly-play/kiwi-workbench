from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseDriver(ABC):
    """
    Abstract Base Class for all GUI/Browser Automation Drivers.
    Drivers simulate human interactions (GUI) rather than API calls.
    """
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the driver with configuration.
        
        Args:
            config (dict): A dictionary containing configuration.
        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """
        Check if necessary config keys are present.
        """
        pass
