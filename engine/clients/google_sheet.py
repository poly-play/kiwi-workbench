import os
import gspread
from typing import List, Dict, Any, Union
import pandas as pd
from engine.clients.base_client import BaseClient

class GoogleSheetClient(BaseClient):
    """
    Client for interacting with Google Sheets using gspread.
    Automatically authenticates using GOOGLE_APPLICATION_CREDENTIALS env var.
    """
    
    def _validate_config(self):
        # Check if auth file is set in env
        self.auth_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not self.auth_file:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. Please set it in .env pointing to your service account json.")
        
        # Initialize gspread
        try:
            self.client = gspread.service_account(filename=self.auth_file)
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with Google Sheets: {e}")

    def open_sheet(self, key_url_or_title: str):
        """
        Open a Google Sheet by Key, URL, or Title.
        """
        try:
            if key_url_or_title.startswith("http"):
                return self.client.open_by_url(key_url_or_title)
            # Heuristic: Keys are usually long alphanumeric, titles are readable words
            # But gspread methods are specific. 
            # We'll try open (by title) first if it looks like a title, or just fallback order.
            try:
                return self.client.open_by_key(key_url_or_title)
            except gspread.exceptions.APIError: # Invalid key format
                return self.client.open(key_url_or_title)
        except gspread.exceptions.SpreadsheetNotFound:
            # Try opening by title as last resort if not key
            try:
                 return self.client.open(key_url_or_title)
            except gspread.exceptions.SpreadsheetNotFound:
                raise ValueError(f"Spreadsheet not found. identifier: {key_url_or_title}. Did you share it with the service account?")

    def read_as_dataframe(self, sheet_key_or_url: str, worksheet_name: str = None, worksheet_gid: int = None) -> pd.DataFrame:
        """
        Read a worksheet into a Pandas DataFrame.
        Priority: worksheet_name > worksheet_gid > First Sheet.
        """
        sh = self.open_sheet(sheet_key_or_url)
        
        ws = None
        if worksheet_name:
            ws = sh.worksheet(worksheet_name)
        elif worksheet_gid is not None:
            # GSpread doesn't have direct get_by_id usually, iterate
            for w in sh.worksheets():
                if w.id == worksheet_gid:
                    ws = w
                    break
            if not ws:
                raise ValueError(f"Worksheet with GID {worksheet_gid} not found.")
        else:
            ws = sh.sheet1
            
        data = ws.get_all_values()
        if not data:
            return pd.DataFrame()
            
        headers = data.pop(0)
        return pd.DataFrame(data, columns=headers)

    def write_dataframe(self, df: pd.DataFrame, sheet_key_or_url: str, worksheet_name: str, clear_existing: bool = True):
        """
        Write a Pandas DataFrame to a worksheet.
        """
        sh = self.open_sheet(sheet_key_or_url)
        
        try:
            ws = sh.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create if not exists
            ws = sh.add_worksheet(title=worksheet_name, rows=100, cols=20)
            
        if clear_existing:
            ws.clear()
            
        # Update with headers
        ws.update([df.columns.values.tolist()] + df.values.tolist())

    def find_spreadsheet_in_folder(self, title: str, folder_id: str):
        """
        Find a spreadsheet by title within a specific folder using Drive API.
        Returns the spreadsheet object (gspread.Spreadsheet) or None.
        """
        try:
            q = f"'{folder_id}' in parents and name = '{title}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
            params = {"q": q, "fields": "files(id, name)"}
            res = self.client.http_client.request("GET", "https://www.googleapis.com/drive/v3/files", params=params)
            files = res.json().get('files', [])
            
            if files:
                # Return the first match
                return self.client.open_by_key(files[0]['id'])
            return None
        except Exception:
            return None

    def create_spreadsheet(self, title: str, folder_id: str = None):
        """
        Create a new spreadsheet.
        If folder_id is provided, creates it inside that folder.
        """
        if folder_id:
            return self.client.create(title, folder_id=folder_id)
        return self.client.create(title)

    def share_spreadsheet(self, sheet_key_or_url: str, email: str, role: str = 'writer', type: str = 'user'):
        """
        Share the spreadsheet with a user or group.
        Args:
            sheet_key_or_url: The sheet identifier
            email: User email to share with
            role: 'reader', 'writer', 'owner'
            type: 'user', 'group', 'domain', 'anyone'
        """
        sh = self.open_sheet(sheet_key_or_url)
        sh.share(email, perm_type=type, role=role)

    def append_row(self, sheet_key_or_url: str, values: List[Any], worksheet_name: str = None):
        """
        Append a single row to the worksheet.
        """
        sh = self.open_sheet(sheet_key_or_url)
        if worksheet_name:
            ws = sh.worksheet(worksheet_name)
        else:
            ws = sh.sheet1
        ws.append_row(values)
