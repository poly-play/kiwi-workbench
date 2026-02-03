import os
import pymysql
from sshtunnel import SSHTunnelForwarder
from typing import Dict, Any, Optional
from pathlib import Path

class RemoteDBConnector:
    """
    Connects to a remote database, automatically establishing an SSH tunnel if configured.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tunnel = None
        self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        db_config = self.config.get('database', {})
        
        # Check for SSH Tunnel configuration
        tunnel_config = db_config.get('ssh_tunnel', {})
        use_tunnel = tunnel_config.get('enabled', False)

        host = db_config.get('host', '127.0.0.1')
        port = db_config.get('port', 9030) # Default Doris/MySQL port
        user = os.environ.get('DB_USER') or db_config.get('user')
        password = os.environ.get('DB_PASSWORD') or db_config.get('password')
        db_name = db_config.get('db_name')

        if use_tunnel:
            print(f"[Info] Establishing SSH Tunnel via {tunnel_config.get('ssh_alias')}...")
            
            # Resolve ~/.ssh/config
            ssh_config_path = os.path.expanduser('~/.ssh/config')
            
            self.tunnel = SSHTunnelForwarder(
                ssh_address_or_host=tunnel_config.get('ssh_alias'), # Uses ~/.ssh/config alias
                ssh_config_file=ssh_config_path,
                remote_bind_address=(tunnel_config.get('remote_host'), tunnel_config.get('remote_port', 9030)) 
            )
            self.tunnel.start()
            print(f"[Success] Tunnel established. Local bind port: {self.tunnel.local_bind_port}")
            
            # Override host/port to point to local tunnel
            host = '127.0.0.1'
            port = self.tunnel.local_bind_port

        print(f"[Info] Connecting to database {db_name} at {host}:{port}...")
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("[Success] Connected to database.")

    def execute_query(self, query: str, params: tuple = None):
        if not self.conn:
            raise ConnectionError("Not connected to database.")
        
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            print("[Info] Database connection closed.")
        
        if self.tunnel:
            self.tunnel.stop()
            print("[Info] SSH Tunnel closed.")

if __name__ == "__main__":
    # Test stub
    pass
