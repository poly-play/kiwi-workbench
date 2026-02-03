---
description: 每日手动执行 JeetUp 广告消耗对账与日报推送 (ADC + UD)
---

此 Workflow 用于手动触发每日广告消耗对账流程。
它将读取各代投 (ADC, UD) 的 Google Sheet，生成统一日报，并推送到 Lark 群组。

### 1. Dry Run (模拟运行)
首先进行模拟运行，检查数据读取是否正常，并预览日报内容。不会写入文件或发送真实通知。

```bash
uv run --project engine engine/scripts/domain/marketing/acquisition/agency_reconciliation.py --app jeetup --env prod --region in --dry-run
```

### 2. Production Run (正式运行)
确认预览无误后，执行正式运行。这将：
1. 生成 CSV 报表到 `data/outputs/marketing/jeetup/`
2. 推送中文日报到 Lark 群组

```bash
uv run --project engine engine/scripts/domain/marketing/acquisition/agency_reconciliation.py --app jeetup --env prod --region in
```
