import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

def to_class_name(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))

def scaffold(domain, sub_domain, job_name, description):
    # 1. Validate Paths
    target_dir = PROJECT_ROOT / "engine" / "scripts" / "domain" / domain / sub_domain
    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist. Please check domain/sub_domain validity.")
        sys.exit(1)
        
    target_file = target_dir / f"{job_name}.py"
    if target_file.exists():
        print(f"Error: Script {target_file} already exists.")
        sys.exit(1)
        
    # 2. Read Template
    tpl_path = PROJECT_ROOT / "engine" / "templates" / "script.py.jinja2"
    with open(tpl_path, 'r') as f:
        content = f.read()
        
    # 3. Replace (Simple string replace for zero deps)
    class_name = to_class_name(job_name)
    content = content.replace("{{ClassName}}", class_name)
    content = content.replace("{{domain}}", domain)
    content = content.replace("{{sub_domain}}", sub_domain)
    content = content.replace("{{job_name}}", job_name)
    content = content.replace("{{description}}", description)
    
    # 4. Write
    with open(target_file, 'w') as f:
        f.write(content)
        
    print(f"✅ Created: {target_file}")
    
    # 5. Register in Library
    register_script(job_name, domain, sub_domain, description, target_file)
    
    print(f"Run with: uv run --project engine {target_file} --app <app>")

def register_script(name, domain, sub_domain, description, path):
    import yaml
    
    lib_path = PROJECT_ROOT / "knowledge" / "script_library.yaml"
    if not lib_path.exists():
        print("Warning: script_library.yaml not found. Skipping registration.")
        return

    try:
        with open(lib_path, 'r') as f:
            data = yaml.safe_load(f) or {"scripts": []}
            
        # Check for duplicates
        scripts = data.get("scripts", [])
        for s in scripts:
            if s['name'] == name:
                print(f"Script {name} is already registered.")
                return
                
        # Append
        rel_path = path.relative_to(PROJECT_ROOT)
        new_entry = {
            "name": name,
            "domain": domain,
            "sub_domain": sub_domain,
            "description": description,
            "path": str(rel_path)
        }
        scripts.append(new_entry)
        data["scripts"] = scripts
        
        with open(lib_path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            
        print(f"📘 Registered in knowledge/script_library.yaml")
        
    except Exception as e:
        print(f"Failed to register script: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: scaffold.py <domain> <sub_domain> <job_name> <description>")
        sys.exit(1)
    
    scaffold(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
