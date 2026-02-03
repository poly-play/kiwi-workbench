---
description: 验证代码是否符合 Kiwi Workbench 工程规范 (包括 BaseScript, Dry Run, 中文通知等)
---

此 Workflow 用于审计和校准代码是否符合 `workbench_standards.md` 定义的工程规范。
请按照以下步骤检查目标脚本 (默认检查当前活跃文件)。

### 1. 确认目标文件
询问用户需要检查的脚本路径。如果是最近编辑的文件，可以直接开始。

### 2. 执行静态审计 (Static Audit)
使用 `view_file` 读取脚本内容，重点检查以下 7 个关键点：

1.  **类继承 (Class Inheritance)**:
    *   必须继承自 `BaseScript` (`from engine.scripts.core.base_script import BaseScript`)
    *   必须定义 `DOMAIN` 和 `JOB_NAME` 类属性。
2.  **Dry Run 支持**:
    *   必须在 `run()` 方法中检查 `self.dry_run`。
    *   在 Dry Run 模式下，**严禁**执行副作用操作 (写文件、发真实请求)，除非是安全读操作。
    *   Dry Run 必须能够跑通核心逻辑并输出预览日志。
3.  **配置加载 (Config Loading)**:
    *   必须使用 `self.config` (由 `BaseScript` 自动加载)。
    *   严禁硬编码敏感信息 (API Key, URL)，应从 Config 或 ENV 读取。
4.  **通知规范 (Notification)**:
    *   通知内容必须为 **中文**。
    *   `self.notifier.send(..., key="...")` 中的 Key 必须对应 `config.yaml` 中的 `business_domains`。
5.  **输出规范 (Output)**:
    *   必须使用 `self.out` (`OutputManager`) 管理文件输出路径。
    *   严禁直接写死 `/tmp` 或相对路径。
6.  **导入路径 (Import Paths)**:
    *   如果是深层目录脚本，检查是否包含 `sys.path` 修正逻辑 (如果有必要)。
    *   检查是否规范引用 `engine` 模块。
7.  **代码风格**:
    *   是否有清晰的注释。
    *   方法是否单一职责。

### 3. 执行动态验证 (Dynamic Verification)
如果静态检查通过，尝试运行脚本的 `--dry-run` 模式进行验证。

```bash
PYTHONPATH=. uv run --project engine PATH/TO/SCRIPT.py --app {APP} --env {ENV} --region {REGION} --dry-run
```

### 4. 生成审计报告
如果发现问题，生成一份修复清单或直接进行代码修正 (Multi-Replace)。
如果完全合规，输出 "✅ 此代码符合 Kiwi 工程规范"。
