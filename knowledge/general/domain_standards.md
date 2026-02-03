# iGaming 业务域标准 (Business Domain Standards)

为了统一配置管理、日志审计与通知路由，Kiwi 将所有业务脚本划分到以下 5 个标准业务域中。
请在编写脚本、配置 Notification Config 时严格遵循此标准。

## 1. 核心业务域 (Core Domains)

> **知识库参考**: 
> *   📖 **[行业术语表 (Glossary)](knowledge/general/glossary.md)**: GGR, NGR, Wager, MAB 等定义。
> *   🧮 **[指标计算标准 (Metrics)](knowledge/general/metrics_standards.md)**: 公式标准 (如 NGR = GGR - Bonus - Tax)。

| 业务域 Code | 中文名称 | 定义范围 | 典型场景 |
| :--- | :--- | :--- | :--- |
| **`operations`** | 用户运营 | 涉及用户生命周期、留存、活动与客服相关的操作。 | 发奖 (Survey Rewards)、VIP 升级、批量发信、用户标签管理。 |
| **`marketing`** | 市场投放 | 涉及广告投放、素材管理、渠道归因与代理商数据。 | 素材上传 (CreativeOps)、渠道数据抓取、ROI 分析报告。 |
| **`risk`** | 风控安全 | 涉及反欺诈、设备指纹、资金安全与合规审计。 | 刷号检测、大额提现预警、IP 关联分析、设备黑名单。 |
| **`finance`** | 财务对账 | 涉及三方支付 (PSP) 对账、资金流水与盈亏报表。 | 通道对账、每日盈亏 (PnL) 计算、钱包余额监控。 |
| **`tech`** | 技术运维 | 涉及系统监控、基建配置与自动化脚本维护。 | 服务器状态检查、数据库备份、证书续期。 |

## 2. 细分业务域 (Sub-Domains)

为了进一步隔离不同职能的数据与通知，请使用 **`Domain.SubDomain`** 的二级结构（例如 `marketing.creative`）。以下是推荐的细分标准：

### 2.1 Marketing (市场)
| 子域 (SubDomain) | 定义 | 典型脚本 |
| :--- | :--- | :--- |
| **`creative`** | **素材中心 (CreativeOps)** | 自动化标签 (Tags)、素材去重、ROI 关联分析。 |
| **`acquisition`** | **广告投放 (Paid UA)** | 渠道消耗对接 (MMP/Media)、归因数据清洗、ROAS 监控。 |
| **`affiliate`** | **代理/通过 (Affiliates)** | 佣金结算 (CPA/RevShare)、代理商防作弊、链接管理。 |
| **`organic`** | **自然流量 (SEO/ASO)** | 关键词排名监控、域名健康度检查、社媒数据抓取。 |

### 2.2 Operations (运营)
| 子域 (SubDomain) | 定义 | 典型脚本 |
| :--- | :--- | :--- |
| **`activity`** | **活动运营 (Campaigns)** | 发奖、活动配置、榜单结算、节日大促。 |
| **`retention`** | **存量运营 (Lifecycle)** | **生命周期管理**(新手/活跃/流失)、CRM 触达、召回任务。 |
| **`vip`** | **大客户 (High Value)** | 升降级处理、大客户生日礼金、专属客服流、定制红利。 |
| **`game`** | **游戏/内容 (Content)** | 游戏上下架、RTP 监控、首页楼层排序、维护公告。 |

### 2.3 Risk (风控)
| 子域 (SubDomain) | 定义 | 典型脚本 |
| :--- | :--- | :--- |
| **`fraud`** | **反欺诈 (Anti-Fraud)** | 刷号检测、多账号关联 (IP/Device)、红利套利识别。 |
| **`payment`** | **支付风控 (Payment)** | 通道成功率监控、大额提现审核、拒付 (Chargeback) 预警。 |
| **`compliance`** | **合规 (Compliance)** | KYC 完整性检查、AML 反洗钱扫描、自我排查。 |

### 2.4 Finance (财务)
| 子域 (SubDomain) | 定义 | 典型脚本 |
| :--- | :--- | :--- |
| **`reconciliation`** | **对账 (Reconciliation)** | PSP 通道三方对账、银行流水核对、差异平账。 |
| **`treasury`** | **资金管理 (Treasury)** | 钱包余额监控、备付金调拨、汇率损益计算。 |
| **`accounting`** | **财务核算 (Accounting)** | 每日盈亏 (PnL)、代理商分红计算、税费预估。 |

### 2.5 Tech (技术)
| 子域 (SubDomain) | 定义 | 典型脚本 |
| :--- | :--- | :--- |
| **`infra`** | **运维/监控** | 证书续期、API 延迟监控、服务器资源巡检。 |
| **`data`** | **数据工程** | ETL 任务、数据备份、报表预计算。 |

## 3. 目录与路由规范

### 3.1 脚本与产出目录 (Directory Structure)
必须遵循 `{Domain}/{SubDomain}/` 的物理层级：
*   ✅ **Script**: `engine/scripts/domain/operations/activity/survey_rewards.py`
*   ✅ **Output**: `data/outputs/operations/activity/{YYYY-MM}/...`
*   ✅ **Store**: `data/store/operations/activity/db/tracking.db` (持久化数据)

### 3.2 通知道由逻辑
配置 `business_domains` 时建议精确到子域。Notifier 会按以下顺序回退查找：
1.  **精确匹配**: 查找 `marketing.creative`
2.  **父域兜底**: 查找 `marketing`
3.  **全局默认**: 查找 `default_channels`

### 3.3 数据库规范 (Database Standards)
**原则**：SQLite 用于存储“轻量级本地状态”或“资产元数据”，严禁用于替代真正的 Data Warehouse。

1.  **System Level (`data/store/system/db/`)**
    *   **用途**: 全局基础设施共用的状态。
    *   **例子**: `audit.db` (执行日志), `asset_ops.db` (素材索引)。
    *   **访问**: 通过 `engine.utils` 或 `AssetManager` 封装访问。

2.  **Domain Level (`data/store/{Domain}/{SubDomain}/db/`)**
    *   **用途**: 特定脚本或业务流的“记忆”。
    *   **例子**: `tracking.db` (记录谁领过奖励，防止重复发)。
    *   **访问**: 在脚本中使用 `self.get_store_path("db", "filename.db")` 获取路径。
    *   **生命周期**: 随业务脚本存亡，不应被其他 Domain 直接依赖（Loose Coupling）。

**Config 示例**:
```yaml
notifications:
  business_domains:
    # 精确路由：素材组有独立的飞书群
    "marketing.creative": ["lark_creative_group"]
    
    # 兜底路由：其他市场相关脚本发到市场大群
    "marketing": ["lark_marketing_general"]
```
