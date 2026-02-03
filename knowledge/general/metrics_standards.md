# iGaming 指标计算标准 (Metrics Standards)

为了保证财务对账和数据分析的一致性，所有脚本和报表必须严格遵循以下计算公式。

## 1. 收入类 (Revenue)

### 1.1 GGR (Gross Gaming Revenue)
`GGR = 投注额 (Bet) - 派彩额 (Win)`

*   **注意**: 不包含任何红利扣除、不包含 Jackpot 贡献。
*   **正负性**: GGR > 0 代表平台盈利；GGR < 0 代表平台亏损。

### 1.2 NGR (Net Gaming Revenue)
`NGR = GGR - Bonus Cost - Admin Fee - Tax`

*   **Bonus Cost**: 已被消耗的红利 + 现金返水。
*   **Tax**: 各国监管税费 (L2 Config)。
*   **Admin Fee**: 平台费/游戏厂商分成 (Game Provider Revenue Share, e.g. PGSoft 10%)。

### 1.3 资金流 (Fund Flow)

#### 1.3.1 充提差 (Cash Net Deposit)
`Cash Net = Total Deposit (Success) - Total Withdrawal (Success)`

*   **定义**: 仅计算**已完成**的资金变动。
*   **用途**: **财务对账**。衡量实际银行账户的资金增减。
*   **特性**: 每日波动较大，受财务打款速度影响（例如昨天的提现今天才打款，会拉低今天的充提差）。

#### 1.3.2 净充值 (Management Net Deposit)
`Mgmt Net = Total Deposit (Success) - Total Withdrawal (Success + Pending/Audit)`

*   **定义**: 扣除了**在途提现** (已申请但未打款) 的净额。
*   **用途**: **经营分析**。衡量业务当天的真实表现。
*   **逻辑**: 用户申请提现时，虽然钱还没划走，但在业务逻辑上这笔钱已经“不属于”平台了，必须扣除，否则会虚高当日业绩。

#### 1.3.3 提现率 (Withdrawal Rate)
`Withdrawal Rate = Total Withdrawal (Mgmt View) / Total Deposit`

*   **口径**: 统一采用 **Management View** (Success + Pending) 计算。
    *   *理由*: 只要用户发起了提现，无论财务是否打款，都代表了用户的“离场意愿”。
    *   *公式*: `(提现成功 + 提现审核 + 提现在途) / 充值成功`

*   **行业基准**:
    *   **优秀**: < 50% (玩家粘性高，钱留住了)
    *   **正常**: 50% - 70% (杀率正常)
    *   **亏损**: > 100% (被掏空了，需要查是自然爆奖还是被攻击)

## 2. 运营类 (KPIs)

### 2.1 留存率 (Retention Rate)
`Day N Retention = (Day N 还在投注的用户数) / (Day 0 FTD 用户数)`

*   **关键定义**: "还在" 指的是 **Bet Event**，不是 Login Event。

### 2.2 ARPU vs ARPPU
*   **ARPU (Average Revenue Per User)**: `Total Revenue / Total Active Users`。
*   **ARPPU (Average Revenue Per Paying User)**: `Total Revenue / Total Depositing Users`。
*   *Insight*: ARPPU 衡量大R付费能力，ARPU 衡量整体盘子。

## 3. 风险类 (Risk)

### 3.1 损益比 (Win/Loss Ratio)
`Ratio = Total Win / Total Bet`

*   **正常范围**: 95% ~ 98% (根据 RTP)。
*   **异常**: 如果某玩家 Ratio > 200% 且 Bet > 1000，**高风险**。

### 3.2 提存比 (Withdrawal/Deposit Ratio)
`W/D Ratio = Total Withdrawal / Total Deposit`

*   **健康线**: 一般 < 70%。
*   **警戒线**: > 100% (平台在净流出)。
*   **个例**: 单个用户 > 500% 且是新号 -> 重点查是否套利。

## 4. 代理渠道 (Affiliate)

### 4.1 NGR (for Commission)
代理佣金计算通常采用调整后的 NGR：
`Affiliate NGR = GGR - Bonus - Processing Fee (充提手续费)`

*   **Processing Fee**: 通常定为充值的 2% + 提现的 2%。这是为了防止代理为了赚佣金刷流水导致的通道费亏损。
