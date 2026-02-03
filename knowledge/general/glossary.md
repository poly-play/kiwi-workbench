# iGaming 行业通用术语表 (Glossary)

本文档旨在统一团队（运营/技术/AI）对行业黑话的理解。

## 1. 玩家与账户 (Player & Account)

*   **KYC (Know Your Customer)**: 实名认证过程，通常包括身份证、地址证明。
    *   *Risk Note*: 提现前的必经之路，防止未成年或欺诈。
*   **MAB (Monthly Active Bettors)**: 月活跃投注用户。
    *   *Data Note*: 注意是 "Bettors" (有下注行为)，而非仅仅 "Login" (登录)。
*   **Whale (鲸鱼/大客)**: 高净值 VIP 玩家。
*   **Bonus Abuser (刷子)**: 利用红利漏洞套利的恶意玩家。
*   **Multi-Accounting (多账号)**: 同一实体控制多个账户，主要用于刷首充红利。

## 2. 资金与交易 (Finance & Transaction)

*   **FTD (First Time Deposit)**: 首充。衡量获客质量的核心指标。
*   **RD (Return Deposit)**: 复充。衡量留存质量的核心指标。
*   **GGR (Gross Gaming Revenue)**: 总博彩收入。
    *   `GGR = Total Bets - Total Wins` (平台赢的钱，还没扣红利)。
*   **NGR (Net Gaming Revenue)**: 净博彩收入。
    *   `NGR = GGR - Bonuses - Taxes - Commissions` (真正的利润)。
*   **Chargeback (拒付)**: 玩家通过银行撤销交易。这是 Payment 最大的风险指标。
*   **PSP (Payment Service Provider)**: 三方支付渠道 (如 PIX 代理, USDT 网关)。

## 3. 运营与市场 (Ops & Marketing)

*   **Wager / Rollover (流水)**: 玩家提现前必须达到的投注额。
    *   *Example*: 充 100 送 100，20倍流水。则玩家需下注 `(100+100)*20 = 4000` 才能提现。
*   **Rebate / Cashback (返水)**: 基于流水或亏损返还给玩家的现金。
    *   `Rolling Rebate`: 基于流水 (无论输赢都给)。
    *   `Loss Rebate`: 基于亏损 (救济金)。
*   **CPA (Cost Per Acquisition)**: 按人头付费的广告/代理模式。
*   **RevShare (RS)**: 按 NGR 分成的代理模式。
*   **LTV (Life Time Value)**: 用户全生命周期价值。
    *   `LTV = ARPU * Retention Lifetime`。

## 4. 技术与合规 (Tech & Compliance)

*   **RTP (Return to Player)**: 玩家返还率。
    *   *Target*: 老虎机通常 95%-97%。如果某天 RTP > 100%，说明平台亏钱了（被爆大奖）。
*   **RNG (Random Number Generator)**: 随机数生成器，游戏公平性的基石。
*   **AML (Anti-Money Laundering)**: 反洗钱。
    *   *Rule*: 存款必须 1倍流水 才能提现。这是为了防止有人把赌场当银行过账。
