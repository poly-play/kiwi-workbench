import os
import io
from typing import Optional, List, Dict
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from engine.clients.base_client import BaseClient

class GoogleDriveClient(BaseClient):
    """
    Client for interacting with Google Drive using the Official Google Python API.
    Handles user auth (OAuth 2.0) for personal accounts or Service Accounts.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def _validate_config(self):
        # Path to secrets
        # Assuming engine structure: engine/clients/../../secrets
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        token_path = os.path.join(project_root, 'secrets', 'google_drive_token.json')
        
        self.creds = None

        # 1. Try User Credentials (token.json) - Preferred for Uploads
        if os.path.exists(token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                # Auto-refresh if expired
                if self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
            except Exception as e:
                print(f"[Warn] User token found at {token_path} but invalid: {e}")
        
        # 2. Fallback to Service Account (GOOGLE_APPLICATION_CREDENTIALS)
        if not self.creds:
            self.auth_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if self.auth_file:
                try:
                    self.creds = service_account.Credentials.from_service_account_file(
                        self.auth_file, scopes=self.SCOPES
                    )
                except Exception as e:
                    pass
        
        if not self.creds:
             raise ValueError("No valid credentials found. Please run 'engine/scripts/setup/google_auth.py' to login as user, or set GOOGLE_APPLICATION_CREDENTIALS.")

        try:
            self.service = build('drive', 'v3', credentials=self.creds)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Drive Client: {e}")

    def upload_file(self, 
                    local_path: str, 
                    folder_id: Optional[str] = None, 
                    mime_type: Optional[str] = None,
                    new_name: Optional[str] = None) -> Dict:
        """
        Uploads a file to Google Drive.
        Args:
            local_path: Path to the local file.
            folder_id: (Optional) ID of the folder to upload to. None = Root.
            mime_type: (Optional) Specific MIME type. If None, auto-detected.
            new_name: (Optional) Rename file on Drive.
        Returns:
            Dict containing 'id', 'name', 'webViewLink'.
        """
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")
            
        file_name = new_name or os.path.basename(local_path)
        
        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]
            
        # Use simple upload or resumable depending on size? 
        # MediaFileUpload defaults to resumable=True for larger files usually, 
        # but we can force it.
        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return file
        except Exception as e:
            raise RuntimeError(f"Failed to upload file {local_path}: {e}")

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """
        Creates a folder.
        Args:
            name: Folder name.
            parent_id: (Optional) Parent folder ID.
        Returns:
            The created folder's ID.
        """
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        try:
            file = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            return file.get('id')
        except Exception as e:
            raise RuntimeError(f"Failed to create folder '{name}': {e}")

    def find_file(self, name: str, parent_id: Optional[str] = None) -> Optional[Dict]:
        """
        Finds a file or folder by name.
        Returns the first match metadata or None.
        """
        q = f"name = '{name}' and trashed = false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
            
        try:
            response = self.service.files().list(
                q=q,
                spaces='drive',
                fields='nextPageToken, files(id, name, webViewLink)',
                pageSize=1
            ).execute()
            
            files = response.get('files', [])
            return files[0] if files else None
        except Exception as e:
            raise RuntimeError(f"Failed to search for file '{name}': {e}")

    def share_file(self, file_id: str, email: str, role: str = 'writer', type: str = 'user'):
        """
        Shares a file with a user or group.
        Args:
            file_id: The ID of the file/folder.
            email: Email address.
            role: 'reader', 'writer', 'owner', 'commenter'.
            type: 'user', 'group', 'domain', 'anyone'.
        """
        # Batching could be better but single request is fine for now
        def callback(request_id, response, exception):
            if exception:
                # Handle error
                print(f"[Warn] Failed to share file: {exception}")

        batch = self.service.new_batch_http_request(callback=callback)
        
        user_permission = {
            'type': type,
            'role': role,
            'emailAddress': email
        }
        
        try:
            self.service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields='id',
            ).execute()
        except Exception as e:
            raise RuntimeError(f"Failed to share file {file_id} with {email}: {e}")
