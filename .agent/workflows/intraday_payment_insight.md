---
description: 运行所有核心 App (AE + SA) 的实时日内支付分析。用于发现紧急的成功率下跌。
---

# 日内支付洞察工作流 (Intraday Payment Insight)

以 `intraday` 模式运行支付洞察脚本（今日 vs 昨日同时段对比）。

1. 运行 Falcowin (AE) 日内洞察
   // turbo
   `uv run --project engine engine/scripts/domain/risk/payment/payment_insight.py --app falcowin --region ae --env prod --period today`

2. 运行 Kanzplay (SA) 日内洞察
   // turbo
   `uv run --project engine engine/scripts/domain/risk/payment/payment_insight.py --app kanzplay --region sa --env prod --period today`
