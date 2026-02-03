import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import shutil
from engine.scripts.core.base_script import BaseScript

class AgentConfigManager(BaseScript):
    DOMAIN = "tech"
    SUB_DOMAIN = "config"
    JOB_NAME = "agent_config_manager"
    
    NOTIFY_ON_SUCCESS = True # Notify user when config changes happen
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--action", 
            choices=["audit", "fix", "create_skill", "create_workflow", "create_rule"],
            required=True,
            help="Action to perform"
        )
        parser.add_argument(
            "--name", 
            help="Name of the skill, workflow, or rule to create (required for create actions)"
        )

    def run(self):
        action = self.args.action
        
        if action == "audit":
            return self._audit()
        elif action == "fix":
            return self._fix()
        elif action.startswith("create_"):
            if not self.args.name:
                raise ValueError(f"--name is required for {action}")
            return self._create_resource(action, self.args.name)
            
    def _audit(self):
        """Check for configuration health."""
        root = self.paths.project_root
        agent_dir = root / ".agent"
        
        report = {
            "status": "OK",
            "issues": [],
            "checked": []
        }
        
        # Check 1: .agent directory structure
        required_dirs = ["rules", "skills", "workflows"]
        for d in required_dirs:
            p = agent_dir / d
            if not p.exists():
                report["issues"].append(f"Missing directory: .agent/{d}")
                report["status"] = "WARNING"
            else:
                report["checked"].append(f".agent/{d} exists")
                
        # Check 2: Deprecated .cursor/rules
        cursor_rules = root / ".cursor" / "rules"
        if cursor_rules.exists():
             report["issues"].append("Deprecated config found: .cursor/rules (Should be in .agent/rules/)")
             report["status"] = "WARNING"
             
        # Check 3: Skill structure validity
        if (agent_dir / "skills").exists():
            for skill_path in (agent_dir / "skills").iterdir():
                if skill_path.is_dir():
                    if not (skill_path / "SKILL.md").exists():
                        report["issues"].append(f"Invalid skill structure: {skill_path.name} missing SKILL.md")
                        report["status"] = "WARNING"

        print(f"--- Audit Report ({report['status']}) ---")
        for issue in report["issues"]:
            print(f"[!] {issue}")
        if not report["issues"]:
            print("All checks passed.")
            
        return report

    def _fix(self):
        """Fix common configuration issues."""
        root = self.paths.project_root
        agent_dir = root / ".agent"
        fixed = []
        
        # Fix 1: Create directories
        for d in ["rules", "skills", "workflows"]:
            p = agent_dir / d
            if not p.exists():
                if self.dry_run:
                    print(f"[Dry Run] Would create directory: {p}")
                else:
                    p.mkdir(parents=True, exist_ok=True)
                    fixed.append(f"Created .agent/{d}")

        # Fix 2: Move .cursor/rules
        cursor_rules_file = root / ".cursor" / "rules"
        target_rule_file = agent_dir / "rules" / "kiwi_rules.md"
        
        if cursor_rules_file.exists():
            if self.dry_run:
                print(f"[Dry Run] Would move {cursor_rules_file} to {target_rule_file}")
            else:
                # Ensure parent exists
                target_rule_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(cursor_rules_file), str(target_rule_file))
                fixed.append(f"Migrated .cursor/rules to {target_rule_file}")
                
                # Try remove empty .cursor dir
                try:
                    cursor_dir = root / ".cursor"
                    if not any(cursor_dir.iterdir()):
                        cursor_dir.rmdir()
                        fixed.append("Removed empty .cursor directory")
                except Exception:
                    pass

        return {"fixed": fixed}

    def _create_resource(self, action, name):
        """Scaffold new resources."""
        root = self.paths.project_root
        agent_dir = root / ".agent"
        
        target_path = None
        content = ""
        
        if action == "create_skill":
            skill_dir = agent_dir / "skills" / name
            target_path = skill_dir / "SKILL.md"
            content = f"""---
name: {name}
description: [Short description of what this skill does]
---

# {name} Skill

[Detailed instructions for the agent on how to use this skill]
"""
            if not self.dry_run:
                skill_dir.mkdir(parents=True, exist_ok=True)
                
        elif action == "create_workflow":
            target_path = agent_dir / "workflows" / f"{name}.md"
            content = f"""---
description: [Short description of workflow]
---
1. [Step 1]
2. [Step 2]
"""
        elif action == "create_rule":
            target_path = agent_dir / "rules" / f"{name}.md"
            content = f"""# Rule: {name}

[Define the rule content here]
"""
            
        if target_path:
            if target_path.exists():
                raise FileExistsError(f"Target already exists: {target_path}")
                
            if self.dry_run:
                print(f"[Dry Run] Would create file at {target_path} with content:\n{content}")
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content)
                print(f"Created {target_path}")
                
            return {"created": str(target_path)}
            
if __name__ == "__main__":
    AgentConfigManager().execute()
