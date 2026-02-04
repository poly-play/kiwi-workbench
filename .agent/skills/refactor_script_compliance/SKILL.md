---
name: refactor_script_compliance
description: 指导 Agent 将非标准脚本重构为符合 Kiwi 标准的现代脚本（含 TDD 和人工审批）。
---

# Refactor Script Compliance Skill

此技能用于指导 Agent 按照严格的工程标准，将 legacy 脚本升级为符合 `BaseScript` 规范的生产级脚本。

## 适用场景
*   需要将独立 Python 脚本合入 `engine` 项目时。
*   需要为老旧脚本补充 `dry-run` 保护时。
*   需要汉化老旧脚本的输出时。

## 核心流程 (The 5-Step Pipeline)

Agent 必须严格遵守以下执行顺序：

### Phase 1: 深度分析与备份 (Analyze & Backup)
1.  **Read**: 使用 `view_file` 读取目标脚本。
2.  **Backup**: 在同目录下创建 `{filename}.bak` 备份文件（除非用户显式跳过）。
3.  **Audit**: 对照以下列表检查差距：
    *   [ ] **Inheritance**: 继承 `BaseScript`?
    *   [ ] **Safety**: 包含 `dry-run` 逻辑?
    *   [ ] **Localization**: 输出中文日志?
    *   [ ] **Config Strategy**: 硬编码参数 -> `self.config` / Env Vars?
    *   [ ] **Data Taxonomy**:
        *   Human Reports -> `data/outputs` (`self.out`)?
        *   Machine State -> `data/store` (SQLite/JSON)?

### Phase 2: 测试驱动开发 (TDD)
**原则**: 重构不改变外部行为 (Refactoring implies preserving behavior)。

1.  **Create Test**: 在 `tests/` 或同级目录创建临时测试脚本 `test_{script_name}.py`。
2.  **Implement Case**:
    *   **Data Script**: Mock 输入数据 -> 运行 Main 函数 -> Assert 输出文件内容。
    *   **API Script**: Mock `requests` -> 运行函数 -> Assert 调用参数。
3.  **Verify Baseline**: 运行测试，确保在“未修改”状态下通过测试 (Green)。

### Phase 3: 制定计划与审批 (Plan & Gatekeep)
1.  **Draft Plan**: 编写详细的重构包括：
    *   **Metadata**: 类名定义 (`DOMAIN`, `JOB_NAME`)。
    *   **Config**: 硬编码 API Key/URL -> 迁移至 YAML 或 `.env`。
    *   **Storage**: 
        *   `df.to_csv('/tmp/...')` -> `self.out.get_path(...)` (Human Readable).
        *   `sqlite3.connect('my.db')` -> `data/store/{domain}/{app}/my.db` (Machine State).
    *   **Safety**: 副作用 (`write`, `post`) 的 `dry-run` 守卫代码片段。
    *   **Lang**: 汉化映射表 (English -> Chinese)。
2.  **Notify User**: 使用 `notify_user` 提交计划、备份确认和测试通过证明。
    *   **"我已备份代码并跑通基准测试。这是我的重构计划，请批准。"**
3.  **Wait**: 等待用户批准。

### Phase 4: 执行重构 (Refactor)
1.  **Apply Changes**: 使用 `replace_file_content` 分步实施。
2.  **Pattern**:
    ```python
    from engine.scripts.core.base_script import BaseScript

    class MyScript(BaseScript):
        def run(self):
            # ...
            if not self.dry_run:
                perform_action()
            else:
                self.logger.info("[Dry Run] Skip action")
    ```

### Phase 5: 回归验证 (Verify)
1.  **Run Test**: 再次运行 Phase 2 的测试脚本。
2.  **Check Output**: 必须全绿 (Pass)。
3.  **Run Dry-Run**: 手动运行一次脚本的 `--dry-run` 模式，检查日志输出是否为中文且无乱码。
4.  **Cleanup**: 删除备份文件和临时测试脚本。
