import os
import shutil
import hashlib
import sqlite3
import mimetypes
import uuid
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple, List

# Inherit from BaseScript for standardization
from engine.scripts.core.base_script import BaseScript
from engine.scripts.utils.paths import get_store_root, get_tmp_root

# Constants
SYSTEM_DB_DIR = get_store_root() / 'system' / 'db'
DB_PATH = SYSTEM_DB_DIR / 'asset_ops.db'
SCHEMA_PATH = SYSTEM_DB_DIR / 'schema.sql'

class AssetManager(BaseScript):
    DOMAIN = "system"
    SUB_DOMAIN = "assets"
    JOB_NAME = "asset_manager"
    
    """
    Unified Asset Hub Manager.
    Handles Ingestion (Local) and Upload (Cloud).
    Supports Multi-Tenancy via --app logic.
    """

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='command', help='Action')
        
        # Ingest Command
        ingest = subparsers.add_parser('ingest', help='Ingest a single file')
        ingest.add_argument('--file', required=True, help='Path to source file')
        ingest.add_argument('--target_domain', default='marketing', help='Business Domain (e.g. marketing)')
        ingest.add_argument('--target_sub', default='creative', help='Sub Domain (e.g. creative)')
        
        # Inbox Command
        subparsers.add_parser('inbox', help='Scan and ingest from data/tmp')
        
        # Upload Command (Placeholder for future R2 logic)
        upload = subparsers.add_parser('upload', help='Upload asset to Cloud')
        upload.add_argument('--id', required=True, help='Asset ID')

    def run(self):
        self._init_db()
        
        if self.args.command == 'ingest':
            aid = self.ingest(self.args.file, self.args.target_domain, self.args.target_sub)
            return {"status": "success", "action": "ingest", "asset_id": aid}
            
        elif self.args.command == 'inbox':
            processed = self.scan_inbox()
            return {"status": "success", "action": "inbox", "count": len(processed), "ids": processed}
            
        elif self.args.command == 'upload':
            # Future implementation
            return {"status": "pending", "message": "Upload logic not yet implemented"}
            
        else:
            print("No command specified. Use --help.")
            return {"status": "no_action"}

    # --- Core Logic ---

    def _get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        if not os.path.exists(SYSTEM_DB_DIR):
             os.makedirs(SYSTEM_DB_DIR, exist_ok=True)
             
        conn = self._get_connection()
        try:
            # Ensure Table Exists
            # Added 'app_name' column for isolation
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    file_hash TEXT,
                    original_name TEXT,
                    mime_type TEXT,
                    size_bytes INTEGER,
                    local_path TEXT,
                    category TEXT,
                    app_name TEXT,
                    r2_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def _calculate_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def ingest(self, source_path: str, domain: str = 'marketing', sub_domain: str = 'creative') -> str:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        file_hash = self._calculate_hash(source_path)
        file_size = os.path.getsize(source_path)
        mime_type, _ = mimetypes.guess_type(source_path)
        original_name = os.path.basename(source_path)
        
        # Determine App Context (from BaseScript args)
        app_name = self.args.app # Mandatory now
        
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check Dedup (Per App? Or Global? Assets usually Global de-dup saves space)
        # But for strict isolation, we should dedup per app OR just store physically separate even if hash same.
        # Let's do: Global Dedup for Storage Efficiency (Store in 'common'?), OR Strict Isolation.
        # README says: data/store/.../{App}/assets.
        # So we MUST store in App folder.
        
        # Check if this exact file exists for THIS app
        cursor.execute("SELECT id FROM assets WHERE file_hash = ? AND app_name = ?", (file_hash, app_name))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            print(f"[Info] Asset exists for {app_name}. ID: {existing['id']}")
            return existing['id']

        # Path Construction: data/store/{domain}/{sub}/{app}/assets/{yyyy}/{mm}/
        now = datetime.now()
        yyyy = now.strftime('%Y')
        mm = now.strftime('%m')
        _, ext = os.path.splitext(source_path)
        if not ext: ext = ""
        
        # Use BaseScript's helper? 
        # BaseScript.get_store_path works for "store_type/filename".
        # We need "assets/yyyy/mm/filename".
        # Let's use get_store_root() and build manually to be safe.
        
        # Path: store/domain/sub/app/assets/yyyy/mm
        store_dir = get_store_root() / domain / sub_domain / app_name / 'assets' / yyyy / mm
        os.makedirs(store_dir, exist_ok=True)
        
        target_filename = f"{file_hash}{ext}"
        target_path = store_dir / target_filename
        
        # Copy
        shutil.copy2(source_path, target_path)

        # DB Record (System DB tracks all)
        asset_id = str(uuid.uuid4())
        category_tag = f"{domain}.{sub_domain}"
        # Relative path for display/link
        rel_path = str(target_path.relative_to(get_store_root()))
        
        try:
            cursor.execute("""
                INSERT INTO assets (id, file_hash, original_name, mime_type, size_bytes, local_path, category, app_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (asset_id, file_hash, original_name, mime_type, file_size, rel_path, category_tag, app_name))
            conn.commit()
            print(f"[Success] Ingested to {rel_path}. ID: {asset_id}")
            return asset_id
        except Exception as e:
            conn.rollback()
            if os.path.exists(target_path):
                os.remove(target_path)
            raise e
        finally:
            conn.close()        

    def scan_inbox(self) -> List[str]:
        # Enforce App Isolation: data/tmp/{app}/
        if not self.args.app:
            print("[Error] App context required for inbox scanning (use --app).")
            return []

        inbox_dir = get_tmp_root() / self.args.app
        if not inbox_dir.exists():
            print(f"[Info] Inbox empty for {self.args.app} (dir {inbox_dir} missing).")
            return []
            
        files = [f for f in os.listdir(inbox_dir) if os.path.isfile(inbox_dir / f) and not f.startswith('.')]
        print(f"Processing {len(files)} files from Inbox for App: {self.args.app}...")
        
        processed = []
        for filename in files:
            path = str(inbox_dir / filename)
            try:
                # Heuristic: Default to marketing.creative
                domain, sub = 'marketing', 'creative'
                if 'finance' in filename.lower(): domain, sub = 'finance', 'account'
                
                aid = self.ingest(path, domain, sub)
                processed.append(aid)
                os.remove(path)
            except Exception as e:
                print(f"[Error] Failed {filename}: {e}")
        return processed

if __name__ == "__main__":
    AssetManager().execute()
