from typing import Dict, Any, Optional
from .base import BaseConnector
from .sql import SQLConnector
from .gsheet import GSheetConnector

class ConnectorFactory:
    @staticmethod
    def get_connector(name: str, config: Dict[str, Any]) -> BaseConnector:
        source_type = config.get('type')
        config['name'] = name # Inject name for logging
        
        if source_type in ['mysql', 'postgresql', 'doris']:
            return SQLConnector(config)
        
        if source_type == 'google_sheet':
            return GSheetConnector(config)
            
        raise ValueError(f"Unknown datasource type: {source_type}")
