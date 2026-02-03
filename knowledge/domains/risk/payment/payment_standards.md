# Payment Domain Standards (GCC Region)

> **适用范围**: `finance.payment`
> **核心逻辑**: GCC 地区采用了 "Hybrid Aggregation" 架构，即部分通道直连 (Direct)，部分通道通过 OnePay 聚合。

## 1. 接入架构 (Architecture)

### 1.1 路由模式 (Routing)
支付路由分为两层：
1.  **L1 Aggregator**:
    *   **Direct (直连)**: App 直接对接三方 PSP。
    *   **OnePay (聚合)**: App 对接自研聚合网关 OnePay，由 OnePay 再转发给 PSP。
2.  **L2 Channel**: 具体的支付通道供应商 (Provider)。

### 1.2 渠道映射表 (Channel Mapping)
根据 `recharge_channel` 字段判定 L1 路由：

| Channel ID | Route Type | 说明 |
| :--- | :--- | :--- |
| **7** | **OnePay** | 聚合路由。具体的 PSP 信息需读取 `upstream_channel` 字段。 |
| **0, 3, 6, 10...** | **Direct** | 直连路由。ID 本身同时也代表了 PSP。 |

## 2. 供应商分类 (Provider Taxonomy)

### 2.1 OnePay 聚合通道 (Route=OnePay)
当 `recharge_channel = 7` 时，根据 `upstream_channel` 细分：

| Upstream Channel (Raw) | Sub-Channel Name | 说明 |
| :--- | :--- | :--- |
| `PlusPay%` | **PlusPay** | OnePay 路由下的 PlusPay |
| `Buzi%` | **BuziPay** | 包含 AED, USD 等多币种通道 |
| `NoWallet` | **NoWallet** | 极简支付模式 |
| (其他) | *(Keep Raw)* | 其他长尾通道直接透传名称 |

### 2.2 直连通道 (Route=Direct)
当 `recharge_channel != 7` 时，ID 对应关系如下：

| ID | Sub-Channel Name | 说明 |
| :--- | :--- | :--- |
| 0 | **TPay** | |
| 3 | **MePay_AED** | |
| 6 | **TtPay_AED** | |
| 10 | **PlusPay** | 直连模式下的 PlusPay |
| 11 | **BuziPay_AED** | |
| 16 | **NoWallet** | 直连模式下的 NoWallet |
| 19 | **BuziPay_AED2** | BuziPay 备用通道 |
| 22 | **BuziPay_USD** | |

> **注意**: 同一个供应商 (如 PlusPay) 可能同时存在于 OnePay 和 Direct 两种路由中。分析时需区分 `Route` 维度。

## 3. 核心指标 (Core Metrics)

### 3.1 订单状态 (Order Status)
*   **1 (Success)**: 支付成功。
*   **0 (Pending)**: 支付中 (用户已拉起支付但在输入密码，或 PSP 处理中)。
*   **2 (Failed)**: 支付失败 (余额不足、风控拦截、超时)。

### 3.2 计算公式
*   **Total Orders**: `COUNT(*)` (包含所有状态)
*   **Success Count**: `SUM(order_status = 1)`
*   **Success Rate (SR)**: `Success Count / Total Orders * 100%`
*   **Avg Latency**: `AVG(completed_time - created_time)` (仅计算 Success 订单)

## 4. 分析场景 (Analysis Scenarios)

### 4.1 通道健康度监控
*   **维度**: `Route` + `Sub-Channel`
*   **阈值**:
    *   SR < 30%: **Critical** (可能通道挂了)
    *   Latency > 300s: **Warning** (回调延迟高)

### 4.2 路由对比 (A/B Test)
*   对比 **Direct PlusPay** vs **OnePay PlusPay** 的成功率，决策是否切量。

## 5. 支付方式 (Pay Method)
对应数据库字段 `pay_method`，常见值包括：
*   **VISA/MASTERCARD**: 国际信用卡
*   **MADA**: 沙特本地卡
*   **KNET**: 科威特本地卡
*   **Benefit**: 巴林本地卡
*   **STCPay/Urpay**: 电子钱包

> **分析建议**: 在分析具体通道表现时，必须下钻到 `pay_method` 维度，因为同一个通道对不同卡种的支持能力差异巨大。
