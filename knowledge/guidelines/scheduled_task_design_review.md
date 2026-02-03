# 定时任务设计评审 (Scheduled Task Design Review)

## 1. 概述
当前设计采用了 **GitOps 驱动、基于 Crontab** 的调度系统。
- **真理源 (Source of Truth)**: `knowledge/scheduler.yaml`
- **执行引擎**: 本地系统 Cron (`crontab`)
- **隔离机制**: 使用 `uv run` 进行项目级隔离。

## 2. 最佳实践分析

### ✅ 优势 (Strengths)
1.  **GitOps 与版本控制**: 调度表是代码 (`.yaml`)，而不是隐藏在服务器配置中。这使得回滚和审计变得非常容易。
2.  **抽象层**: `scheduler.py` 脚本对 `crontab -e` 进行了封装，防止了人工操作的语法错误。
3.  **原生多租户支持**: `matrix` (Apps x Envs) 的支持完美契合了项目的多租户架构。
4.  **错误可观测性**: `BaseScript` 的集成确保了 *应用层* 的错误会触发飞书 (Lark) 通知，避免了 Crontab 常见的“静默失败”问题。

### ⚠️ 风险与不足 (Risks & Gaps)
1.  **并发控制缺失 (Concurrency Control)**:
    - **风险**: 如果一个任务 (`frequency: 1h`) 运行耗时超过 1.5 小时，`cron` 会启动第二个实例。这可能导致竞态条件 (Race Conditions) 或数据库死锁。
    - **修复**: 在 `scheduler.py` 或 `BaseScript` 中实现 `flock` 文件锁或 PID 检查机制。
2.  **单点故障 (SPoF)**:
    - **风险**: 系统完全依赖于本地机器的守护进程。
    - **背景**: 对于“单机工作台”还可以接受，但需要监控（例如：增加一个“心跳”任务）。
3.  **重试机制**:
    - **风险**: 瞬时故障（如网络抖动）会导致任务失败，直到下一次调度周期。目前没有自动重试/退避策略。
4.  **环境稳定性**:
    - **风险**: 生成的 Crontab 依赖于绝对路径 (`/Users/mark/...`)。如果文件夹移动，调度器将失效。

## 3. 结论 (Verdict)
**这是否符合最佳实践？**
*   **对于企业级/分布式系统**: **否**。(通常会使用 Airflow / Temporal)。
*   **对于单节点运营工作台**: **是**。它遵循 **KISS (Keep It Simple, Stupid)** 原则。在当前规模下引入 Airflow 属于过度设计。

## 4. 建议 (Recommendations)
1.  **增加安全保障 (建议)**:
    - 增加 **文件锁 (File Lock)** 机制，防止重叠执行。
    - 示例: `flock -n /tmp/myjob.lock uv run ...`
2.  **增加心跳监控**:
    - 每小时调度一个简单的任务，向死人开关 (Dead-man switch) 或 Lark 发送信号，证明调度守护进程仍在运行。
