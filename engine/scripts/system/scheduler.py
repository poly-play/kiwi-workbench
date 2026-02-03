import yaml
import sys
import subprocess
import argparse
from pathlib import Path

# Setup Path to allow imports if needed, though this script is self-contained mainly.
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

def load_registry():
    yaml_path = PROJECT_ROOT / "knowledge" / "scheduler.yaml"
    if not yaml_path.exists():
        print(f"Registry not found at {yaml_path}")
        return {}
    
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f) or {}

def generate_cron_lines(config: dict):
    lines = []
    lines.append("# BEGIN KIWI_SCHEDULER_BLOCK (Managed by Kiwi Engine)")
    lines.append(f"# Updated at: {subprocess.check_output(['date']).decode().strip()}")
    lines.append("SHELL=/bin/bash") # Ensure bash for uv
    lines.append(f"KIWI_ROOT={PROJECT_ROOT}") 
    lines.append("")
    
    jobs = config.get('jobs', {})
    if not jobs:
        lines.append("# No jobs scheduled.")
    
    for job_id, spec in jobs.items():
        script_rel = spec.get('script')
        cron_expr = spec.get('cron')
        desc = spec.get('description', job_id)
        
        if not script_rel or not cron_expr:
            print(f"Skipping invalid job {job_id}")
            continue
            
        # Matrix Expansion
        matrix = spec.get('matrix', {})
        apps = matrix.get('apps', [])
        envs = matrix.get('envs', ['prod']) # Default to prod
        
        # If no matrix apps, maybe single run? 
        # But BaseScript requires --app. 
        # If user didn't specify apps, we skip or warn.
        if not apps:
            print(f"Skipping job {job_id}: No apps specified in matrix.")
            continue
            
        lines.append(f"# Job: {job_id} - {desc}")
        
        script_abs = PROJECT_ROOT / "engine" / "scripts" / script_rel
        if not script_abs.exists():
             print(f"WARNING: Script not found: {script_abs}")
             lines.append(f"# WARNING: Script not found {script_rel}")
             continue

        for app in apps:
            for env in envs:
                # Command Construction
                # uv run --project {root}/engine {script} --app {app} --env {env}
                # redirect stdout/stderr to log? relying on BaseScript generic logging?
                # BaseScript logs to DB/Lark. But cron output (print) goes to mail usually.
                # Let's silence or redirect to /dev/null to prevent mailbox spam, 
                # as BaseScript handles its own logging.
                
                # Concurrency Control: Use lockf to prevent overlapping execution
                # Lock File: /tmp/kiwi_{job_id}_{app}_{env}.lock
                lock_file = f"/tmp/kiwi_{job_id}_{app}_{env}.lock"
                
                # Params Injection
                extra_args = []
                params = spec.get('params', {})
                for k, v in params.items():
                    extra_args.append(f"--{k} {v}")
                extra_args_str = " ".join(extra_args)
                
                # Command: lockf -t 0 /tmp/xxx /bin/bash -c "cd ... && uv run ..."
                # We wrap the actual work in bash -c to handle cd and redirection safely within the lock context (or getting the lock first).
                # Actually, lockf executes the command. 
                # Added {extra_args_str} to command
                inner_cmd = f"cd '{PROJECT_ROOT}' && /Users/mark/.local/bin/uv run --project engine '{script_abs}' --app {app} --env {env} {extra_args_str} >> '{PROJECT_ROOT}/data/outputs/cron.log' 2>&1"
                
                # Escape double quotes for the bash -c string if necessary, but paths usually don't have them. 
                # Safe usage: /usr/bin/lockf -t 0 {lock_file} /bin/bash -c "{inner_cmd}"
                final_cmd = f"/usr/bin/lockf -t 0 {lock_file} /bin/bash -c \"{inner_cmd}\""
                
                lines.append(f"{cron_expr} {final_cmd}")
        
        lines.append("")
        
    lines.append("# END KIWI_SCHEDULER_BLOCK")
    return lines

def get_current_crontab():
    try:
        return subprocess.check_output(["crontab", "-l"]).decode().splitlines()
    except subprocess.CalledProcessError:
        return [] # Empty crontab

def update_crontab(new_block_lines):
    current = get_current_crontab()
    
    # Remove old block
    final_lines = []
    in_block = False
    found_block = False
    
    for line in current:
        if "# BEGIN KIWI_SCHEDULER_BLOCK" in line:
            in_block = True
            found_block = True
            continue
        if "# END KIWI_SCHEDULER_BLOCK" in line:
            in_block = False
            continue
            
        if not in_block:
            final_lines.append(line)
            
    # Append new block
    final_lines.extend(new_block_lines)
    
    # Write back
    content = "\n".join(final_lines) + "\n"
    
    p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
    p.communicate(input=content.encode())
    
    print("Crontab updated successfully.")

def main():
    parser = argparse.ArgumentParser(description="Kiwi Scheduler Manager")
    parser.add_argument("action", choices=["sync", "preview"], help="Action to perform")
    args = parser.parse_args()
    
    registry = load_registry()
    new_lines = generate_cron_lines(registry)
    
    if args.action == "preview":
        print("\n".join(new_lines))
    elif args.action == "sync":
        update_crontab(new_lines)

if __name__ == "__main__":
    main()
