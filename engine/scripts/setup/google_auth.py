
import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.append(project_root)

# Paths
SECRETS_DIR = os.path.join(project_root, 'secrets')
TOKEN_FILE = os.path.join(SECRETS_DIR, 'google_drive_token.json')

# Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_client_secret_file():
    """Finds the client secret file (exact match or glob)."""
    # 1. Exact default
    default_path = os.path.join(SECRETS_DIR, 'client_secret.json')
    if os.path.exists(default_path):
        return default_path
    
    # 2. Search for client_secret*.json
    import glob
    candidates = glob.glob(os.path.join(SECRETS_DIR, 'client_secret*.json'))
    if candidates:
        return candidates[0] # Return the first one found
    
    return None

def main():
    print("🔐 Authorization Setup for Kiwi")
    print("-------------------------------")
    
    client_secret_file = get_client_secret_file()
    
    if not client_secret_file:
        print(f"❌ Error: No 'client_secret*.json' found in {SECRETS_DIR}.")
        print("   Please create OAuth credentials in Google Cloud, download the JSON, and place it here.")
        return

    print(f"📂 Using Client Secret: {os.path.basename(client_secret_file)}")

    creds = None
    # 1. Check existing token
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print("found existing credentials.")
        except Exception:
            print("Existing credentials invalid, ignoring.")

    # 2. Refresh or Login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Refresh failed ({e}), initiating new login.")
                creds = None
        
        if not creds:
            print("🚀 Launching browser for login...")
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, SCOPES
            )
            # Run local server
            creds = flow.run_local_server(port=0)
            
        # 3. Save Token
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f"✅ Authentication successful! Token saved to: {TOKEN_FILE}")
    else:
        print("✅ Credentials are valid. No action needed.")

if __name__ == '__main__':
    main()
