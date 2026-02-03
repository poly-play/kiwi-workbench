---
name: update_knowledge
description: 知识更新标准流程。当用户作为“上下文提供者”注入新的业务逻辑或规则时，请使用此技能。
---

# 知识更新协议 (Update Knowledge Protocol)

## 1. 技能描述
本技能定义了创建或更新知识库文档的标准流程。
当用户扮演“上下文提供者 (Context Provider)”的角色，向你注入新的业务逻辑、运营规则或配置参数时，你必须遵循此流程。它的核心目的是维护 **“单一事实来源 (Single Source of Truth)”** 原则。

## 2. 前置条件 (Prerequisites)
- **意图分析 (Intent Analysis)**: 首先判断用户提供的是什么？
    - **规则 (Rule)**: 适用于所有 App 的通用逻辑（如：洗码公式）。
    - **配置 (Config)**: 特定 App 的参数（如：JeetUp 的商户号）。
    - **定义 (Definition)**: 数据指标的定义（如：怎么算“活跃用户”）。

## 3. 使用说明 (Usage)
这是一个 **元技能 (Meta-Skill)**，即操作流程，而非单一的 CLI 命令。

### 目录分类规则 (Taxonomy Rules)
- `knowledge/domains/`: **业务逻辑** (例如: `marketing/rebate_policy.md` - 返佣策略)。
- `knowledge/platforms/`: **应用配置** (例如: `jeetup/payment_channels.md` - 支付通道)。
- `knowledge/guidelines/`: **工程标准** (例如: `code_style.md` - 代码规范)。

### 执行步骤 (Execution Steps)
1.  **检索 (Search)**: 永远先搜索现有的相关文件。不要制造重复。
2.  **定位 (Locate)**: 根据意图，将新知识归类到正确的目录。
3.  **起草 (Draft)**: 使用清晰的 Markdown 标题和表格。
4.  **审计 (Audit)**: 检查新知识是否与旧规则冲突。

## 4. 示例 (Examples)

**场景: 用户想要更新 VIP 返佣比例。**
1.  在 `knowledge/` 中搜索 "rebate" (返佣)。
2.  找到了 `knowledge/domains/marketing/rebate_policy.md`。
3.  **操作**: 在该文件中追加新的比例表格，或者替换旧表格。
4.  **禁忌**: **绝对不要** 创建一个叫 `new_rebate_rules_2024.md` 的新文件（这会导致碎片化）。

## 5. 故障排除与注意事项 (Troubleshooting)
- **处理冲突**: 如果新知识违反了现有的 `guidelines`（标准），请询问用户：“这是要更新标准（创新），还是您的输入有误（错误）？”
- **命名规范**: 始终使用 `snake_case.md` (蛇形命名法)。
