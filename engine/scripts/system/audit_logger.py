import sqlite3
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Constants
from engine.scripts.utils.paths import get_store_root
PROJECT_ROOT = Path(__file__).resolve().parents[4] # engine/scripts/system/ -> ROOT
AUDIT_DB_PATH = get_store_root() / "system" / "db" / "audit.db"

class AuditLogger:
    """
    Logs execution events to a central SQLite database.
    """
    def __init__(self):
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(AUDIT_DB_PATH), exist_ok=True)
        with sqlite3.connect(AUDIT_DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    domain TEXT,
                    job_name TEXT,
                    user TEXT,
                    host TEXT,
                    output_path TEXT,
                    status TEXT,
                    meta_json TEXT
                )
            """)

    def log_success(self, domain: str, job_name: str, output_path: str, context: Dict[str, Any]):
        try:
            import json
            import getpass
            import socket
            
            with sqlite3.connect(AUDIT_DB_PATH) as conn:
                conn.execute(
                    """
                    INSERT INTO execution_log 
                    (timestamp, domain, job_name, user, host, output_path, status, meta_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datetime.now().isoformat(),
                        domain,
                        job_name,
                        getpass.getuser(),
                        socket.gethostname(),
                        str(output_path),
                        "SUCCESS",
                        json.dumps(context)
                    )
                )
        except Exception as e:
            print(f"[Error] Failed to write audit log: {e}")
