import argparse
import sys
import traceback
from abc import ABC, abstractmethod
from typing import Dict, Any, List

# Ensure engine is in path if not already
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
    
from engine.scripts.utils.context_loader import loader
from engine.scripts.utils.output_manager import OutputManager
from engine.scripts.utils.notifier import Notifier

import logging

class BaseScript(ABC):
    """
    Abstract base class for all Kiwi Operational Scripts.
    Enforces standardized configuration, output management, and error handling.
    """
    
    # Must be overridden by subclasses
    DOMAIN: str = None
    SUB_DOMAIN: str = None # Optional
    JOB_NAME: str = None
    
    # Allowed Domains (Sync with domain_standards.md)
    VALID_DOMAINS = {'operations', 'marketing', 'risk', 'finance', 'tech'}
    
    # Flags
    NOTIFY_ON_SUCCESS = False
    NOTIFY_ON_FAILURE = True

    def __init__(self):
        self._validate_meta()
        self.args = self._parse_args()
        self.dry_run = self.args.dry_run
        
        # Setup Logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(self.JOB_NAME)
        
        # Load Config
        self.config = loader.load(
            region=self.args.region,
            app=self.args.app,
            env=self.args.env
        )
        
        # Init Output Manager
        job_id = f"{self.JOB_NAME}_{self.args.env}" 
        self.out = OutputManager(
            domain=self.DOMAIN, 
            job_name=job_id, 
            config=self.config,
            sub_domain=self.SUB_DOMAIN,
            app_name=self.args.app 
        )
        
        # Init Notifier
        self.notifier = Notifier(self.config)
        
        # Init Paths Helper
        self.paths = self.PathHelper()

    class PathHelper:
        """Helper to access standard paths."""
        @property
        def project_root(self):
            from engine.scripts.utils.paths import get_project_root
            return get_project_root()
            
        @property
        def knowledge_root(self):
            from engine.scripts.utils.paths import get_knowledge_root
            return get_knowledge_root()
            
        def get_output_root(self, domain: str, sub_domain: str = None):
            from engine.scripts.utils.paths import get_output_root
            return get_output_root(domain, sub_domain)

    def get_connector(self, source_name: str):
        """Helper to get data connector from config."""
        return loader.get_source(source_name, self.config)

    def get_store_path(self, store_type: str, filename: str) -> Path:
        """
        Returns an absolute path to the App-Specific Domain Store.
        Args:
            store_type: 'db', 'files', 'assets'
            filename: Name of the file
        Returns:
            .../data/store/{DOMAIN}/{SUB_DOMAIN}/{APP_NAME}/{store_type}/{filename}
        """
        from engine.scripts.utils.paths import get_store_root
        
        # Determine Routing
        sub = self.SUB_DOMAIN if self.SUB_DOMAIN else "general"
        
        # Multi-Tenant Isolation
        # App is now mandatory via _parse_args
        app_name = self.args.app
        
        # Path: store/domain/sub/app/type/file
        base = get_store_root() / self.DOMAIN / sub / app_name / store_type
        return base / filename

    def _validate_meta(self):
        if not self.DOMAIN or not self.JOB_NAME:
            raise NotImplementedError("Scripts must define DOMAIN and JOB_NAME.")
        
        if self.DOMAIN not in self.VALID_DOMAINS:
            raise ValueError(f"Invalid DOMAIN '{self.DOMAIN}'. Must be one of {self.VALID_DOMAINS}")

    def _parse_args(self):
        parser = argparse.ArgumentParser(description=f"Kiwi Script: {self.JOB_NAME}")
        # Region and Env can have defaults, but App is mandatory for Multi-Tenancy
        parser.add_argument("--region", default="uae", help="Target Region (e.g. uae, br)")
        parser.add_argument("--app", required=True, help="Target App (e.g. sakerwin, jeetup). MANDATORY.")
        parser.add_argument("--env", default="prod", help="Target Environment (e.g. prod, stg)")
        
        # Standard Dry Run Flag
        parser.add_argument("--dry-run", action="store_true", help="Simulate execution without side effects.")
        
        # Allow subclasses to add arguments
        self.add_arguments(parser)
        
        return parser.parse_args()

    def add_arguments(self, parser):
        """Override to add custom arguments."""
        pass

    @abstractmethod
    def run(self):
        """
        Main logic implementation.
        Should return a dictionary of metadata if successful.
        """
        pass

    def execute(self):
        """Entry point. Wraps run() with error handling and notifications."""
        
        # Routing Key for Notifications
        routing_key = f"{self.DOMAIN}.{self.SUB_DOMAIN}" if self.SUB_DOMAIN else self.DOMAIN
        
        try:
            print(f"[{self.JOB_NAME}] Starting execution...")
            if self.dry_run:
                print("⚠️  [DRY RUN MODE] Actions will be simulated. No changes will be committed.")
            
            # --- RUN ---
            result_meta = self.run() or {}
            # -----------
            
            # 1. Save Meta (via OutputManager)
            self.out.save_meta(extra_info=result_meta)
            
            # 2. Notify Success
            if self.NOTIFY_ON_SUCCESS:
                summary = "\n".join([f"{k}: {v}" for k, v in result_meta.items()])
                self.notifier.send(
                    title=f"✅ Job Complete: {self.JOB_NAME}",
                    message=f"Output: {self.out.output_dir}\n{summary}",
                    key=routing_key
                )
            
        except Exception as e:
            # 1. Print Stack Trace
            traceback.print_exc()
            
            # 2. Send Failure Notification
            error_msg = f"Error: {str(e)}\n\nTrace:\n{traceback.format_exc()[-500:]}" # Last 500 chars
            
            if self.NOTIFY_ON_FAILURE:
                self.notifier.send(
                    title=f"❌ Job Failed: {self.JOB_NAME}",
                    message=error_msg,
                    level="ERROR",
                    key=routing_key
                )
            sys.exit(1)

if __name__ == "__main__":
    print("This is an abstract base class. Cannot run directly.")
