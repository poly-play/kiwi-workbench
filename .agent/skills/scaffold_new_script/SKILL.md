---
name: scaffold_new_script
description: 根据模板创建标准化的新 Python 脚本。
---

# 脚本脚手架 (Scaffold New Script)

## 1. 技能描述
此技能用于从 `BaseScript` 模板创建一个新的标准化 Python 脚本。
当用户希望添加新的运营能力（例如：“写个脚本检查 IP 风险”）时，请使用此技能。
它确保文件被放置在正确的 L1/L2 目录层级中 (`engine/scripts/{domain}/{sub_domain}/...`) 并在系统中注册。

## 2. 前置条件 (Prerequisites)
- **分类决策**: 运行前，必须确定逻辑上的 L1 `domain` (域) 和 L2 `sub_domain` (子域)。
- **任务名 (Job Name)**: 脚本的唯一标识符（使用 snake_case 蛇形命名）。

## 3. 使用说明 (Usage)

### 命令 (Command)
```bash
python .agent/skills/scaffold_new_script/scaffold.py {domain} {sub_domain} {job_name} "{description}"
```

### 参数 (Arguments)
- `domain`: L1 业务域 (如 operations, marketing, risk, finance, tech)。
- `sub_domain`: L2 子业务域 (如 activity, retention, fraud)。
- `job_name`: 脚本名称 (snake_case)。
- `description`: 用于文档的简要描述。

## 4. 示例 (Examples)

### 创建大额提现监控
```bash
# 域: risk (风控), 子域: payment (支付)
python .agent/skills/scaffold_new_script/scaffold.py risk payment check_large_withdrawals "Monitors withdrawals > 10k"
```

## 5. 故障排除与注意事项 (Troubleshooting)
- **路径冲突**: 如果目录不存在，工具 *应该* 会自动创建，但请尽量让您的域名匹配现有的惯例。
- **注册**: 此工具会自动更新 `knowledge/script_library.yaml`（如果已实现）。请核实新脚本是否列在其中。
