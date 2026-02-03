from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import pandas as pd

class BaseConnector(ABC):
    """
    Abstract base class for all data connectors.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unnamed_source')

    @abstractmethod
    def connect(self):
        """Establish connection to the source."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection."""
        pass

    @abstractmethod
    def query(self, query_str: str, **kwargs) -> Union[List[Dict], pd.DataFrame]:
        """
        Execute a query and return results.
        For SQL: query_str is SQL.
        For Sheets: query_str could be a range "Shee1!A1:B10" or empty for whole sheet.
        """
        pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
