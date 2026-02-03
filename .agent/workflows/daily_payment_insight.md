---
description: 财务团队的 AI 驱动每日支付分析。
---

此工作流为所有核心 App 运行 AI 支付分析脚本。
它会生成对比报告（昨日 vs 7日平均），使用 Gemini 分析异常，并发送简报到财务 Lark 群组。

1. 运行 Falcowin (阿联酋) 支付分析
   // turbo
   `uv run --project engine engine/scripts/domain/risk/payment/payment_insight.py --app falcowin --region ae --env prod`

2. 运行 Kanzplay (沙特) 支付分析
   // turbo
   `uv run --project engine engine/scripts/domain/risk/payment/payment_insight.py --app kanzplay --region sa --env prod`
