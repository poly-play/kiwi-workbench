---
description: 更新并应用系统定时任务 (Crontab)
---

此工作流将您的 `knowledge/scheduler.yaml` 配置同步到系统的 `crontab` 中。

1. 同步调度器 (Sync Scheduler)
   // turbo
   `uv run --project engine engine/scripts/system/scheduler.py sync`

> **注意**: 此命令可以安全地多次运行。它只会替换 Crontab 中现有的 Nomad 块，而不会创建重复项。
