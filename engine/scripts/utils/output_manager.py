import os
import json
import socket
import getpass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class OutputManager:
    """
    Standardizes output directory creation and metadata tracking.
    Follows SOM Standard: data/outputs/{domain}/{YYYY-MM}/{job_name}_{batch}
    """
    def __init__(self, domain: str, job_name: str, config: Dict[str, Any] = None, sub_domain: str = None, app_name: str = None):
        """
        Args:
            domain: Business Domain (e.g., 'operations', 'risk') - See domain_standards.md
            job_name: Specific job identifier (e.g., 'survey_rewards')
            config: Full configuration dictionary
            sub_domain: Optional Sub-Domain
            app_name: Target App (multi-tenant isolation)
        """
        if not domain or not job_name:
            raise ValueError("Domain and job_name are required.")
            
        self.domain = domain
        self.sub_domain = sub_domain
        self.job_name = job_name
        self.config = config or {}
        
        # Determine Routing Key
        self.routing_key = f"{domain}.{sub_domain}" if sub_domain else domain
        
        # Setup Output Directory: 
        # data/outputs/{domain}/{sub_domain}/{app_name}/{YYYY-MM}/{job_name}_{batch}/
        
        base_path = PROJECT_ROOT / "data" / "outputs" / domain
        if sub_domain:
            base_path = base_path / sub_domain
            
        # Multi-Tenant Layer
        if app_name:
            base_path = base_path / app_name
        else:
            base_path = base_path / "common"
            
        self.timestamp = datetime.now()
        month_str = self.timestamp.strftime("%Y-%m")
        batch_id = self.timestamp.strftime("%d_%H%M%S")
        
        self.output_dir = base_path / month_str / f"{job_name}_{batch_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_path(self, filename: str) -> Path:
        """Returns the full path for a file in the output directory."""
        return self.output_dir / filename

    def save_meta(self, extra_info: Dict[str, Any] = None):
        """
        Generates/saves meta.json.
        """
        # 1. Create Meta Dict
        meta = {
            "timestamp": self.timestamp.isoformat(),
            "job": {
                "domain": self.domain,
                "sub_domain": self.sub_domain,
                "name": self.job_name,
                "output_dir": str(self.output_dir)
            },
            "config_context": self.config.get('_meta', {}),
            "extra": extra_info or {}
        }
        
        # 2. Save JSON
        json_path = self.get_path("meta.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
            
        print(f"[OutputManager] Metadata saved to {json_path}")
