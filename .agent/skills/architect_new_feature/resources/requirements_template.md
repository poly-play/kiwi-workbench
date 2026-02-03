# [Feature/Request Name] 需求规格说明书 (PRD)

## 1. 背景与目标 (Context & Goal)
*   **背景 (Why)**: [简述现状，为什么要提出这个需求？解决了什么痛点？]
*   **目标 (Goal)**: [一句话描述预期的业务价值，例如：将对账时间从 1 小时缩短到 5 分钟。]
*   **业务域 (Domain)**: [Marketing / Risk / Finance / Operations / Saker / Platform]

## 2. 用户故事 (User Stories)
> 格式：作为 **[什么角色]**，我想要 **[做什么]**，以便于 **[达成什么效果]**。

*   作为 **[Role]**，我想要 **[Action]**，以便于 **[Benefit]**。
*   [例如] 作为 **风控专员**，我想要 **每天早上 9 点收到前一天的 IP 异常报告**，以便于 **及时封禁套利账号**。

## 3. 详细需求 (Detailed Requirements)

### 3.1 核心功能 (Functional)
1.  **输入 (Input)**:
    *   [例如] 需要读取哪些数据源？(Doris / Google Sheets / API)
    *   [例如] 用户需要提供什么参数？(Date Range / User ID)
2.  **处理逻辑 (Logic)**:
    *   [例如] 计算公式是什么？
    *   [例如] 异常判断标准是什么？( > 1000 USD? < 50% Success Rate?)
3.  **输出 (Output)**:
    *   [例如] 产出物形式 (CSV / Markdown Message / Alert)
    *   [例如] 发送到哪里？(Lark Group / Email / R2)

### 3.2 非功能需求 (Non-Functional) & SLIs
1.  **时效性**: [例如] 必须在 5 分钟内完成运行。
2.  **频率**: [例如] 每日定时 / 每小时 / 手动触发。
3.  **容错**: [例如] 如果 API 失败，是重试还是立刻报错？

## 4. 验收标准 (Acceptance Criteria)
*   [ ] [Criteria 1: 正常流程测试通过]
*   [ ] [Criteria 2: 异常数据处理符合预期]
*   [ ] [Criteria 3: 产出物格式正确]
