import os
import pymysql
import psycopg2
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder
from typing import Any, Dict, List, Union
import pandas as pd
from .base import BaseConnector

class SQLConnector(BaseConnector):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.type = config.get('type', 'mysql') # mysql or postgresql
        self.tunnel = None
        self.conn = None
        
    def connect(self):
        tunnel_cfg = self.config.get('ssh_tunnel')
        
        db_host = self.config.get('host', '127.0.0.1')
        db_port = self.config.get('port', 3306 if self.type == 'mysql' else 5432)
        
        # 1. Establish SSH Tunnel if needed
        if tunnel_cfg and tunnel_cfg.get('enabled'):
            user_ssh_config = os.path.expanduser('~/.ssh/config')
            print(f"[{self.name}] Opening SSH Tunnel via {tunnel_cfg.get('ssh_alias')}...")
            
            self.tunnel = SSHTunnelForwarder(
                ssh_address_or_host=tunnel_cfg.get('ssh_alias'),
                ssh_config_file=user_ssh_config,
                remote_bind_address=(tunnel_cfg.get('remote_host'), tunnel_cfg.get('remote_port', db_port))
            )
            self.tunnel.start()
            
            # Point DB connection to local tunnel
            db_host = '127.0.0.1'
            db_port = self.tunnel.local_bind_port
            print(f"[{self.name}] Tunnel active at localhost:{db_port}")

        # 2. Connect to Database
        user = os.environ.get(f"{self.name.upper()}_USER") or self.config.get('user')
        password = os.environ.get(f"{self.name.upper()}_PASSWORD") or self.config.get('password') 
        # Fallback to generic DB_USER/DB_PASS if specific ones not found
        if not user: user = os.environ.get('DB_USER')
        if not password: password = os.environ.get('DB_PASSWORD')

        db_name = self.config.get('database')
        
        print(f"[{self.name}] Connecting to {self.type} at {db_host}...")
        
        if self.type == 'mysql' or self.type == 'doris':
            self.conn = pymysql.connect(
                host=db_host,
                port=db_port,
                user=user,
                password=password,
                database=db_name,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
        elif self.type == 'postgresql':
            self.conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=user,
                password=password,
                dbname=db_name,
                cursor_factory=RealDictCursor
            )
        else:
            raise ValueError(f"Unsupported SQL type: {self.type}")

    def query(self, query_str: str, **kwargs) -> pd.DataFrame:
        if not self.conn:
            self.connect()
            
        with self.conn.cursor() as cursor:
            cursor.execute(query_str, kwargs.get('params'))
            res = cursor.fetchall()
            # Convert to DataFrame for easier handling in Analysis
            return pd.DataFrame(res)

    def disconnect(self):
        if self.conn:
            self.conn.close()
        if self.tunnel:
            self.tunnel.stop()
            print(f"[{self.name}] Connection closed.")
