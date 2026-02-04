---
description: Kiwi 系统自我检查与强化 (升级框架/知识 + 审计脚本 + 审计知识)
---

# Kiwi System Self-Check Workflow

此 Workflow 是 Kiwi 工作台的**日常维护与强化程序**。运营同学应定期（或在遇到问题时）运行此流程，以确保工作台处于最新、最健康的状态。

## 核心功能
1.  **System Update**: 升级远程框架与知识库 (Safe Pull)。
2.  **Knowledge Audit**: 检查本地知识库的结构完整性。
3.  **Script Audit**: 扫描核心脚本的合规性。

## 执行步骤

### Step 1: 系统升级 (Update)
调用 `update_framework` 技能，拉取远程最新的代码和知识。
*   **指令**: "请执行 `update_framework` 技能，更新我的工作台。"
*   **注意**: 如果有冲突，请按照技能指引处理。

### Step 2: 知识库体检 (Knowledge Audit)
调用 `knowledge_auditor` 技能，确保知识库没有结构性错误。
*   **指令**: "请执行 `knowledge_auditor` 技能，扫描全库。"
*   **重点检查**: `yaml` 语法、死链、过期的文档。

### Step 3: 脚本合规检查 (Script Audit)
调用 `verify_code_compliance` Workflow，对关键脚本进行抽查。
*   **指令**: "请对 `engine/scripts/` 下最近修改的脚本执行 `/verify_code_compliance`。"
*   **目标**: 确保所有脚本都符合 `BaseScript` 和 `Dry-Run` 标准。

### Step 4: 报告 (Report)
最后，Agent 应汇总一份**《Kiwi 健康诊断报告》**：
*   ✅ 框架版本: [Latest/Behind]
*   ✅ 知识库健康度: [Pass/Issues]
*   ✅ 脚本合规性: [Pass/Issues]
