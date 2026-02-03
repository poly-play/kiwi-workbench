
import os
import sqlite3
import asyncio
from typing import Optional, List, Dict, Any
from telethon import TelegramClient as TelethonClient
from engine.clients.base_client import BaseClient

class TelegramAccountManager:
    """
    Manages Telegram accounts and sessions using SQLite.
    """
    def __init__(self, db_path: str = "data/store/system/telegram_accounts.db"):
        self.db_path = db_path
        self._init_db()
        self._ensure_migrations()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                phone_number TEXT PRIMARY KEY,
                session_path TEXT NOT NULL,
                account_name TEXT,
                status TEXT DEFAULT 'active',
                tags TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _ensure_migrations(self):
        """Simple migration to add account_name if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('ALTER TABLE accounts ADD COLUMN account_name TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # Column likely already exists
            pass
        conn.close()

    def add_account(self, phone_number: str, session_path: str, tags: str = "", account_name: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO accounts (phone_number, session_path, tags, account_name, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(phone_number) DO UPDATE SET
                session_path=excluded.session_path,
                tags=excluded.tags,
                account_name=COALESCE(excluded.account_name, accounts.account_name),
                updated_at=CURRENT_TIMESTAMP,
                status='active'
        ''', (phone_number, session_path, tags, account_name))
        conn.commit()
        conn.close()

    def get_account(self, phone_number: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE phone_number = ?', (phone_number,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # Handle row index based on schema version or use row_factory
            # Since we didn't set row_factory here (it is set in list_accounts), 
            # and schema might vary, let's use list_accounts logic or be careful.
            # actually better to use row_factory for robustness or explicit indices
            # Schema: phone, session, account_name (if new), status, tags, updated_at (if new)
            # Wait, CREATE TABLE order vs ALTER TABLE add column order.
            # ALTER TABLE adds to the end.
            # Let's switch to row_factory for get_account too.
            pass

        # Re-implementing get_account with row_factory for safety
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE phone_number = ?', (phone_number,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def list_accounts(self, tag: str = None, status: str = "active") -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM accounts WHERE status = ?"
        params = [status]
        
        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

class TelegramClient(BaseClient):
    """
    Wrapper around Telethon Client with multi-account support via AccountManager.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_id = int(os.environ.get("TELEGRAM_API_ID") or self.config.get("api_id"))
        self.api_hash = os.environ.get("TELEGRAM_API_HASH") or self.config.get("api_hash")
        
        # Paths
        self.sessions_dir = self.config.get("sessions_dir", "data/store/system/sessions")
        self.db_path = self.config.get("db_path", "data/store/system/telegram_accounts.db")
        
        self.manager = TelegramAccountManager(self.db_path)
        self.client: Optional[TelethonClient] = None
        self.phone_number: Optional[str] = None

    def _validate_config(self):
        if not self.config.get("api_id") and not os.environ.get("TELEGRAM_API_ID"):
            raise ValueError("TELEGRAM_API_ID is missing in env or config")
        if not self.config.get("api_hash") and not os.environ.get("TELEGRAM_API_HASH"):
            raise ValueError("TELEGRAM_API_HASH is missing in env or config")

    async def connect(self, phone_number: str):
        """
        Connect using a specific phone number. 
        The session must already exist in the DB/Manager.
        """
        account = self.manager.get_account(phone_number)
        if not account:
            raise ValueError(f"Account {phone_number} not found. Please run auth script first.")
            
        session_path = account["session_path"]
        if not os.path.exists(session_path + ".session") and not os.path.exists(session_path):
             # Telethon adds .session automatically usually, but we check just in case
             pass

        print(f"[Telegram] Connecting as {phone_number}...")
        self.client = TelethonClient(session_path, self.api_id, self.api_hash)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            raise PermissionError(f"Session for {phone_number} is invalid or expired.")
            
        self.phone_number = phone_number
        print(f"[Telegram] Connected: {phone_number}")

    async def disconnect(self):
        if self.client:
            await self.client.disconnect()

    async def send_message(self, entity: str, message: str):
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")
        await self.client.send_message(entity, message)

    async def get_messages(self, entity: str, limit: int = 10):
        if not self.client:
            raise RuntimeError("Client not connected.")
        return await self.client.get_messages(entity, limit=limit)
