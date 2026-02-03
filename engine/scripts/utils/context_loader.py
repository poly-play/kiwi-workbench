import yaml
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path for engine imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Now we can import from engine...
from engine.scripts.utils.paths import get_knowledge_root
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

class ContextLoader:
    def __init__(self):
        self.knowledge_root = get_knowledge_root()
        # Load .env from project root if available
        if load_dotenv:
            # 1. Engine Root (engine/.env)
            engine_root = Path(__file__).parent.parent.parent
            load_dotenv(engine_root / ".env")
            
            # 2. Project Root (../.env) - Overrides Engine
            project_root = engine_root.parent
            load_dotenv(project_root / ".env")

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Perform variable substitution
            # Pattern: ${VAR_NAME} or ${VAR_NAME:default}
            # Note: This simple regex handles ${VAR}. Complex defaults might need more logic.
            # We will use os.path.expandvars capabilities or custom regex
            
            # Custom regex for ${VAR}
            # We'll use a recursive function to interpolate AFTER loading yaml to handle types correctly?
            # Actually, doing it on the string content BEFORE parsing is safer for simple string subs.
            
            def replace_env(match):
                var_name = match.group(1)
                return os.environ.get(var_name, match.group(0)) # Return original if not found
                
            content = re.sub(r'\$\{([A-Z0-9_]+)\}', replace_env, content)
            
            return yaml.safe_load(content) or {}
        except Exception as e:
            print(f"[WARN] Failed to load config at {path}: {e}")
            return {}

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two config dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    def load(self, region: str, app: str, env: str) -> Dict[str, Any]:
        """
        Loads configuration by merging 4 layers:
        1. Global
        2. Region
        3. App
        4. Environment
        """
        # Layer 1: Global
        config = self._load_yaml(self.knowledge_root / "general" / "config.yaml")

        # Layer 2: Region
        region_path = self.knowledge_root / "platforms" / region
        config = self._merge_configs(config, self._load_yaml(region_path / "config.yaml"))

        # Layer 3: App
        app_path = region_path / app
        config = self._merge_configs(config, self._load_yaml(app_path / "config.yaml"))

        # Layer 4: Environment
        env_path = app_path / env
        
        # Leaf Secrets Loading
        # If a .env exists in the target environment folder, load it with override=True
        # This allows "Context-Aware" secrets (e.g. DB_PASS) to be defined locally.
        leaf_env = env_path / ".env"
        if leaf_env.exists() and load_dotenv:
            # print(f"[Context] Loading leaf secrets from {leaf_env}")
            load_dotenv(leaf_env, override=True)

        config = self._merge_configs(config, self._load_yaml(env_path / "config.yaml"))

        # Inject Context Metadata
        config['_meta'] = {
            'region': region,
            'app': app,
            'env': env,
            'config_path': str(env_path),
            'secrets_path': str(leaf_env) if leaf_env.exists() else None
        }
        
        return config

    def get_source(self, source_name: str, config: Dict = None):
        """
        Returns a DataConnector instance for the given source name.
        Lazy initialization.
        """
        # Lazy import to avoid circular dependencies
        # Assuming engine is in path
        from engine.connectors.factory import ConnectorFactory
        
        # If config is not provided, we should probably load it?
        # But load() requires region/app/env.
        # For utility scripts without specific context, we might rely on a 'default' or pass config in.
        # However, to be useful, let's assume the user passes the loaded config dict, 
        # OR we look into 'datasources' of the provided config.
        
        if config is None:
             raise ValueError("Config dictionary must be provided to get_source (until we have a global context state).")

        datasources = config.get('datasources', {})
        
        if source_name not in datasources:
            raise ValueError(f"Datasource '{source_name}' not defined in config.")
            
        source_config = datasources[source_name]
        return ConnectorFactory.get_connector(source_name, source_config)

# Singleton instance
loader = ContextLoader()
