from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseClient(ABC):
    """
    Abstract Base Class for all External Service Clients (Gemini, Lark, AWS).
    """
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the client with configuration.
        
        Args:
            config (dict): A dictionary containing configuration for this specific service.
                           Usually passed from ContextLoader.config['clients']['service_name'].
        """
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """
        Check if necessary config keys (api_key, endpoint) are present.
        Raise ValueError if missing.
        """
        pass
