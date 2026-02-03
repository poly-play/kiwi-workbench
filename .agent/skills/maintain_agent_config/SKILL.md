---
name: maintain_agent_config
description: Manage Antigravity configuration (Rules, Skills, Workflows). Audit health, fix issues, and scaffold new items.
---

# Maintain Agent Configuration

Use this skill to ensure the Antigravity Agent configuration (`.agent/` directory) is healthy and compliant with standards.

## Capabilities

1.  **Audit Configuration**: Check for missing directories, deprecated file locations (like `.cursor/rules`), and invalid skill structures.
2.  **Fix Configuration**: Automatically fix common issues (e.g., creating directories, migrating files).
3.  **Scaffold Resources**: Create templates for new Skills, Workflows, or Rules using standard naming and directory structures.

## Usage

**ALWAYS** use `app=system` for configuration management tasks.

### 1. Audit Configuration
Run this to check the health of the `.agent` directory.
```bash
uv run --project engine engine/scripts/config/agent_config_manager.py --app system --action audit
```

### 2. Fix Configuration
Run this to automatically fix specific issues (like moving `.cursor/rules` to `.agent/rules/`).
```bash
uv run --project engine engine/scripts/config/agent_config_manager.py --app system --action fix
```

### 3. Create New Skill
Create a new skill folder and `SKILL.md` template.
```bash
uv run --project engine engine/scripts/config/agent_config_manager.py --app system --action create_skill --name <skill_name>
```

### 4. Create New Workflow
Create a new workflow markdown file.
```bash
uv run --project engine engine/scripts/config/agent_config_manager.py --app system --action create_workflow --name <workflow_name>
```

### 5. Create New Rule
Create a new rule markdown file.
```bash
uv run --project engine engine/scripts/config/agent_config_manager.py --app system --action create_rule --name <rule_name>
```
