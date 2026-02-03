import yaml
from pathlib import Path
from engine.scripts.core.base_script import BaseScript

class KnowledgeSyncer(BaseScript):
    DOMAIN = "tech"
    SUB_DOMAIN = "data"
    JOB_NAME = "knowledge_syncer"
    
    def add_arguments(self, parser):
        parser.add_argument("--target_config", help="Relative path to config file to update, e.g. knowledge/platforms/in/jeetup/config.yaml")

    def run(self):
        # 1. Identify Target
        # If no target specified, try to infer from App Context
        # But for safety, let's require it or derive it
        if self.args.target_config:
            target_path = Path(self.args.target_config)
        else:
            # Auto-locate based on App
            # This requires 'loader' to tell us where the config came from, 
            # but loader returns a merged dict.
            # So we better rely on standard convention.
            # Assuming standard structure: knowledge/platforms/{region}/{app}/config.yaml
            # We need 'region' from args.
            if not self.args.region or not self.args.app:
                 raise ValueError("Must provide --region and --app to auto-locate config.")
            
            from engine.scripts.utils.paths import PROJECT_ROOT
            target_path = PROJECT_ROOT / "knowledge" / "platforms" / self.args.region / self.args.app / "config.yaml"

        if not target_path.exists():
            print(f"Target config not found: {target_path}")
            # Optional: Create it? No, sync usually updates existing.
            return {"status": "skipped", "reason": "config_not_found"}

        # 2. Fetch Truth (Simulated)
        # In logic, this would be: 
        # db = self.get_connector('warehouse')
        # fresh_data = db.query("SELECT key, value FROM system_config")
        
        print(f"Syncing knowledge for {self.args.app} from Source of Truth...")
        
        # Mocking acquired data
        fresh_data = {
            "last_synced_at": "NOW()",
            "active_payment_methods": ["pix", "usdt"] if self.args.region == "br" else ["upi", "paytm"],
            "maintenance_mode": False
        }
        
        # 3. Update YAML
        # Round-trip preservation is hard with PyYAML (comments lost).
        # For 'Executable Knowledge', we accept that these specific files are machine-managed.
        
        with open(target_path, 'r') as f:
            current_conf = yaml.safe_load(f) or {}
            
        # Update/Merge
        self._deep_update(current_conf, fresh_data)
        
        with open(target_path, 'w') as f:
            yaml.safe_dump(current_conf, f, default_flow_style=False, allow_unicode=True)
            
        print(f"✅ Updated {target_path}")
        return {"status": "success", "updated_keys": list(fresh_data.keys())}

    def _deep_update(self, base_dict, update_dict):
        for k, v in update_dict.items():
            if isinstance(v, dict) and k in base_dict and isinstance(base_dict[k], dict):
                self._deep_update(base_dict[k], v)
            else:
                base_dict[k] = v

if __name__ == "__main__":
    KnowledgeSyncer().execute()
