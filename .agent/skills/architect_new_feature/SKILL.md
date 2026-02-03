---
description: 按照 Kiwi 标准，通过"咨询-定义-架构-验证"四步法，设计高质量的新功能或自动化流程。
---

# 新功能架构 (Architect New Feature) v2.0

## 1. 技能描述
此技能通过 **"产品交付流水线" (Product Delivery Pipeline)** 将模糊的运营需求转化为确定性的工程实现。
它不仅仅是生成代码结构，更是通过多轮交互确保需求被正确理解和设计。

**核心流程**:
1.  **Consult (咨询)**: 像产品经理一样挖掘需求。
2.  **Define (定义)**: 产出 PRD (`requirements.md`)。
3.  **Architect (架构)**: 产出 TDD (`technical_design.md`)。
4.  **Verify (验证)**: 规划测试与验收标准。

## 2. 前置条件
- 理解 `knowledge/guidelines/kiwi_vision_whitepaper.md` (架构原则)。
- 理解 `knowledge/guidelines/kiwi_vision_whitepaper.md` (架构原则)。
- 能够创建和编辑 Markdown 文件。
- **环境检查**: 确保已运行 `./scripts/setup.sh` 且环境就绪。

## 3. 交互流程 (Interactive Workflow)

作为 Agent，在执行此技能时，必须严格遵循以下 **Step-by-Step** 顺序。不要试图一次性跳过所有步骤。

### Phase 1: 需求咨询 (The Consultant)
**目标**: 澄清模糊需求。不要一上来就写代码！
1.  **主动提问**: 使用 **5-Dimension Heuristics** (Goal, Frequency, Handling, Edge Case, Output) 询问用户。
    *   *Prompt*: "为了设计出最适合您的工具，我需要确认几个细节：这个功能的使用频率是？如果数据异常，您希望如何通知？..."
2.  **生成 PRD**: 当信息收集足够时，基于模板创建需求文档。
    *   **模板**: `.agent/skills/architect_new_feature/resources/requirements_template.md`
    *   **输出**: `workspace/requirements_[feature_name].md`
3.  **用户确认**: 使用 `notify_user` 请求用户确认需求文档。

### Phase 2: 技术方案 (The Architect)
**目标**: 将需求映射为 Kiwi 标准组件。
1.  **架构设计**: 
    *   确定组件类型: Script (L1), Skill (L2), Workflow (L3), Reporter (YAML)。
    *   确定配置层级: Global / Region / App。
2.  **生成 TDD**: 基于模板创建技术设计文档。
    *   **模板**: `.agent/skills/architect_new_feature/resources/technical_design_template.md`
    *   **输出**: `workspace/design_[feature_name].md`
    *   **关键检查点 (Must Validate against `README.md`)**: 
        *   **Data Taxonomy**: 所有的写操作是否都落在了 `data/outputs` (Human) 或 `data/store` (Machine)?
        *   **Multi-Tenancy**: 是否遵循 `Region -> App` 的层级结构？
        *   是否有多租户隔离？
        *   密钥是否使用了环境变量？
        *   是否继承了 `BaseScript`？
        *   **依赖管理**:
            *   如果有新依赖，严禁使用 `pip install`。
            *   必须使用 `uv add [package] --project engine`。

### Phase 3: 验证规划 (The QA)
**目标**: Test-Driven Design。
1.  在 TDD 中完善 **验证计划 (Verification Plan)** 章节。
2.  必须包含 `--dry-run` 的测试场景。

### Phase 4: 移交开发 (Handover)
当且仅当用户**批准技术设计文档**后，你才可以建议用户：
*   "设计已就绪。您是否希望我现在开始开发？(我们可以使用 `scaffold_new_script` 技能)"

## 4. 示例对话 (Example)

**User**: "帮我做一个查大户流失的工具。"

**Agent (Wrong)**: "好的，我这就写代码..." (❌ 未经思考)

**Agent (Correct)**: "收到。为了确保工具精准有效，我们需要先对齐一下需求：
1. 您定义的'大户'标准是什么？(充值 > 1000u?)
2. '流失'是指几天未登录？(7天? 30天?)
3. 这个报告需要每天自动推送到飞书群吗？
在此期间，我将为您起草一份 `requirements_churn_monitor.md`..."

## 5. 故障排除
*   **需求变来变去**: 如果用户在 Phase 2 修改了核心需求，请退回到 Phase 1 更新 PRD。
*   **设计过于复杂**: 始终遵循 KISS 原则。如果一个 Script 能解决，不要搞微服务。
