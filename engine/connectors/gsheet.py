from typing import Any, Dict, List, Union
import pandas as pd
import gspread
import os
from .base import BaseConnector

class GSheetConnector(BaseConnector):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.sheet = None
        
    def connect(self):
        # Authenticate using Service Account or Local Creds
        # For this design, we assume a standard 'credentials.json' or env vars
        # This is simplified for the prototype
        print(f"[{self.name}] Authenticating with Google Sheets...")
        # Check for service account file in env or default location
        creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
        
        if os.path.exists(creds_path):
            self.client = gspread.service_account(filename=creds_path)
        else:
            # Fallback to generic service_account() which looks for standard paths
            try:
                self.client = gspread.service_account() 
            except Exception as e:
                # If no file, maybe we handle OAuth logic later. 
                # For now assume service account.
                raise EnvironmentError(f"Could not find Google Credentials at {creds_path}. Error: {e}")

        spreadsheet_id = self.config.get('spreadsheet_id')
        if not spreadsheet_id:
            raise ValueError("Config missing 'spreadsheet_id'")
            
        self.sheet = self.client.open_by_key(spreadsheet_id)
        print(f"[{self.name}] Opened Sheet: {self.sheet.title}")

    def query(self, query_str: str = "", **kwargs) -> pd.DataFrame:
        """
        query_str: Specific worksheet name or range. 
                   e.g. "Sheet1" or "Sheet1!A1:E"
                   If empty, gets first worksheet.
        """
        if not self.client:
            self.connect()
            
        try:
            if not query_str:
                worksheet = self.sheet.sheet1
            elif '!' in query_str:
                # Parse range? gspread handles A1 notation usually on worksheet
                # Simplified: just get worksheet by name for now
                ws_name = query_str.split('!')[0]
                worksheet = self.sheet.worksheet(ws_name)
            else:
                worksheet = self.sheet.worksheet(query_str)
                
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            print(f"[{self.name}] Error fetching data: {e}")
            raise

    def disconnect(self):
        # gspread uses REST API, no persistent connection to close
        pass
