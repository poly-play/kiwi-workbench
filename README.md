# 🥝 Kiwi: The iGaming Operations Workbench
> **Current Version**: 0.4.0 (Beta)
> **Core Engine**: Antigravity Hybrid-Architecture

Kiwi 是一个为 iGaming 运营量身定制的**智能化工作台**。它旨在通过 standardized workflows (SOP), unified data connectors (UDC), 和 agentic automation，将碎片化的运营工作（如发奖、素材管理、对账）整合成一个高效、可复用的系统。

---

## 📚 知识库与指南 (Guidelines)
我们采用标准化的 "5-Part Taxonomy" 来组织知识：

| 目录 | 英文名 | 作用 | 示例 |
| :--- | :--- | :--- | :--- |
| **`general/`** | **通用标准** | 全局共享的不可变真理 (Source of Truth)。 | 术语表、财务指标计算公式。 |
| **`platforms/`** | **平台配置** | 支撑多租户运行的 L2-L4 配置矩阵。 | Brazil 税率、JeetUp 数据库密码。 |
| **`domains/`** | **业务逻辑** | **[NEW]** 不同业务域的特定规则与字典。 | 支付通道 ID 映射表、风控封号规则。 |
| **`reports/`** | **报表定义** | 这里的 "Code" 是 YAML 格式的 SQL 逻辑。 | `payment_success_analysis.yaml` |
| **`guidelines/`** | **操作指南** | 给人看的说明书 (SOP) 和给 AI 看的协议。 | 知识维护协议 (KMP)、新员工入职手册。 |

> **Best Practice**: 当 AI 遇到不懂的业务逻辑 (例如: ID=7 代表什么?)，**必须**去 `domains/` 下寻找答案，而不是瞎猜。

---

## 1. 概念模型 (Conceptual Model)
Kiwi 的设计遵循 "Pyramid of Automation" 架构：

*   **L3 Workflows (Process)**: `.agent/workflows/` - 编排业务流程 (SOP)。
*   **L2 Skills (Capabilities)**: `.agent/skills/` - 赋予 AI 操作能力 (Tooling)。
*   **L1 Scripts (Logic)**: `engine/scripts/` - 原子业务逻辑 (Execution)。
*   **L0 Knowledge (Context)**: `knowledge/` - 业务规则与配置 (Configuration)。

---

## 2. 快速开始 (Getting Started)

本项目使用 `uv` 进行极速依赖管理。

### 环境准备
1.  **安装 uv**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
2.  **初始化环境**:
    无需手动创建 venv，直接运行以下命令即可自动同步依赖：
    ```bash
    uv sync --project engine
    ```

### 2.2 敏感配置与密钥 (Secrets Management)
为了安全与灵活性，Kiwi 采用 **"双层密钥管理"** 策略：

#### A. 全局基建 (Global Infra)
*   **位置**: 项目根目录 `.env` (从 `.env.example` 复制)。
*   **内容**: **Kiwi 自身的运行环境**。
    *   AI 密钥 (`GEMINI_API_KEY`)
    *   资源存储 (`R2_ACCESS_KEY`)
    *   网络代理 (`HTTPS_PROXY`)

#### B. 业务密钥 (Leaf Secrets)
*   **位置**: 具体环境目录下的 `.env` (如 `knowledge/platforms/br/winner777/prod/.env`)。
*   **内容**: **业务运行所需的凭证**。
    *   数据库密码 (`MYSQL_PASSWORD`)
    *   机器人密钥 (`LARK_SECRET`)
*   **用法**:
    1.  在目标文件夹新建 `.env` 并写入密钥。
    2.  在同级 `config.yaml` 中使用 `${VAR_NAME}` 引用。

#### C. 文件级凭证 (File Secrets)
*   **位置**: 项目根目录下的 `secrets/` 目录。
*   **内容**: **JSON 密钥文件、证书文件**。
    *   Google Service Account (`secrets/google_credentials.json`)
    *   SSL 证书 (`secrets/cert.pem`)
*   **用法**: 直接在代码或配置中引用路径 `secrets/xxxx.json`。

> **安全提示**: 所有 `.env` 文件及 `secrets/` 目录均已被 git 忽略，严禁提交到版本库！

---

## 2. 核心架构：多层级配置 (Multi-Layer Config)
为了支撑多国家 (Multi-Region) 和多应用 (Multi-App) 的业务形态，我们采用**分层配置矩阵**：

| 层级 (Layer) | 定义 | 示例路径 | 作用 |
| :--- | :--- | :--- | :--- |
| **L1 Global** | 行业通用标准 | `knowledge/general/` | 定义 GGR, FTD 等通用术语标准 |
| **L2 Regional** | 区域合规与基建 | `knowledge/platforms/br/` | 巴西的税率, PIX 支付渠道, 时区 |
| **L3 Application** | 具体 App 逻辑 | `.../br/winner777/` | 品牌色, VIP 规则, 活动配置 |
| **L4 Environment** | 运行时环境 | `.../winner777/stg/` | `config.yaml` (逻辑开关) + **`.env` (密码/密钥)** |

> **ContextLoader 原理**：当您执行指令时，系统会自动将这 4 层配置合并（Environment > App > Region > Global），生成当前操作所需的完整上下文。

---

## 3. 多租户设计 (Multi-Tenancy)
> **核心原则**: Shared Logic, Isolated State (代码共享，数据隔离)。

Kiwi 强制实施 App 维度的物理隔离，确保 A 品牌的数据绝对不会泄露给 B 品牌。

### 3.1 设计哲学：业务隔离 > 技术复用 (Isolation > Reuse)
我们宁愿**重复配置 10 次**（copy-paste `.env`），也不愿为了省事而将 10 个业务强耦合在一起。
*   **Code (L1/L2)**: 共享。所有 App 共用一套 Python 脚本和 Skill。
*   **Config (L4)**: 隔离。每个 App 独享一套 `.env` 和 `config.yaml`。哪怕它们连接的是同一个数据库，也要分开配置。

### 3.2 命令行强制隔离
所有脚本在执行时，**必须**指定的目标 App：
```bash
# ✅ 正确：明确指定 app
uv run ... script.py --app jeetup

# ❌ 错误：系统会报错并拒绝执行
uv run ... script.py
```

### 3.2 物理路径隔离
系统会自动将数据分流到对应 App 的专属目录：
*   **持久化存储**: `data/store/{Domain}/{SubDomain}/{App}/db/tracking.db`
*   **产出物归档**: `data/outputs/{Domain}/{SubDomain}/{App}/{YYYY-MM}/...`

### 3.3 虚拟应⽤ (Virtual Apps for Ops)
针对“区域级调研”、“竞品分析”等不属于具体业务 App 的任务，我们采⽤ **Virtual App** 模式，将其视为⼀个特殊的 App。

*   **命名规范**: `{region}_ops` (例如 `br_ops`, `global_ops`)。
*   **作⽤**: 执⾏通⽤任务，如 Telegram 爬⾍、市场调研、竞品监控。
*   **优势**: 完美复⽤现有的隔离架构，无需编写特殊逻辑。

```bash
# 示例：使⽤巴西运营中⼼ (Virtual App) 执⾏竞品分析
uv run ... analysis.py --app br_ops
```

---

## 4. 目录结构 (Directory Structure)

```text
/Users/mark/Projects/igaming operation/
├── .agent/             # [Agent] Skills & Workflows
├── secrets/            # [密钥] 文件级凭证 (Gitignored)
├── knowledge/          # [配置] 4层配置矩阵
├── engine/             # [内核] 代码与依赖
│   └── scripts/
│       ├── domain/     # [业务逻辑] operations, marketing, risk...
│       ├── system/     # [系统组件] scheduler, generic_reporter
│       └── core/       # [基础架构] BaseScript
│   └── clients/        # [三方服务] Gemini, Lark, AWS (Reusable SDKs)
│   └── drivers/        # [GUI模拟] Headless Browser Drivers (Selenium/Playwright)
├── data/               # [数据中心]
│   ├── tmp/            # [Inbox] 临时文件投递区 (Gitignored)
│   ├── outputs/        # [Results] 脚本产出物 (Reports, CSV)
│   │   └── {Domain}/{SubDomain}/{App}/...
│   └── store/          # [Repository] 统一持久化存储
│       ├── system/     # [Global] 审计日志, 资源索引
│       └── {Domain}/{SubDomain}/{App}/  # [Tenant] 租户与业务数据
│           ├── files/  # 文档
│           ├── assets/ # 媒体
│           └── db/     # 状态 (SQLite)
└── workspace/          # [Scratchpad] 临时分析草稿
```

### 4.1 数据分类标准 (Data Taxonomy)
为了回答 **"数据放哪里？"** 的问题，我们确立了以下三分法：

#### (1) Knowledge (大脑/知识库)
*   **路径**: `knowledge/`
*   **定义**: **Worldview & Rules**。只读的业务真理。
*   **内容**: SOP、配置 (`config.yaml`)、**整理好的外部文档** (如竞品报告)。

#### (2) Store (记忆/海马体)
*   **路径**: `data/store/{Domain}/{SubDomain}/{App}/`
*   **定义**: **State & Context**。运行时的草稿和存档。
*   **内容**: Cursor 断点、Cookie、爬虫原始内容 (`raw_html/`)。

#### (3) Output (产出物)
*   **路径**: `data/outputs/{Domain}/{SubDomain}/{App}/{YYYY-MM}/`
*   **定义**: **Deliverables**。交付给人类的结果。
*   **内容**: 日报 CSV、分析报告、图表。**按月自动归档**。

---

## 5. 运营模式 (Operating Model)
为了降低运营人员的使用门槛，我们采用 **"80/20"** 分层策略。

### 5.1 方案 A：通用报表 (80% 需求)
> **适合场景**: "每天跑个 SQL，有异常就发飞书给我。"

*   **特点**: **Zero Code** (配置化)。
*   **用法**: 只需编写一个 YAML 文件，定义 SQL 和报警规则。
*   **示例**:
    ```bash
    # 场景 A: 每日自动跑 (昨日数据)
    uv run ... generic_reporter.py --config knowledge/reports/examples/large_withdrawal.yaml --app jeetup --period yesterday

    # 场景 B: 补跑上个月月报
    uv run ... generic_reporter.py --config ... --period last_month
    ```
    > **Time Travel**: 支持 `today`, `yesterday`, `this_week`, `last_week`, `this_month`, `last_month` 等时间维度参数化。

### 5.2 方案 B：定制脚本 (20% 需求)
> **适合场景**: "复杂的发奖逻辑，要调用第三方 API，还要写数据库。"

*   **特点**: **Low Code** (模版化)。
*   **用法**: 使用 Skill 一键生成标准代码框架。
*   **指令**:
    ```bash
    python .agent/skills/scaffold_new_script/scaffold.py risk fraud check_ip "Check Login IP"
    ```
    (生成后，只需填充 `run()` 方法中的业务逻辑即可)
    > **自动注册**: Scaffolder 会自动将新脚本登记到 `knowledge/script_library.yaml`，确保 Agent 随时知道有哪些工具可用。

---

## 6. 功能模块详解

### 6.1 任务调度 (Scheduler)
采用 **GitOps** 模式管理定时任务。
*   **Registry**: `knowledge/scheduler.yaml` (唯一真理源)
*   **同步指令**: `uv run ... engine/scripts/system/scheduler.py sync`
*   **矩阵执行**: 支持 `apps: [a, b]` 配置，自动为多个 App 生成独立任务。
*   **并发控制 (New)**: 采用 `lockf -t 0` 机制防止任务重叠执行。
    *   锁文件路径: `/tmp/kiwi_{job}_{app}_{env}.lock`
    *   行为: 如果上一轮任务未结束，新任务将自动跳过 (Non-blocking)。

### 6.2 统一资源中心 (Asset Hub)
*   **Local Ingestion**: `uv run ... engine/scripts/system/asset_manager.py ingest` (存入本地，去重)
*   **Cloud Delivery**: `uv run ... engine/scripts/system/asset_manager.py upload` (上传 R2，生成 CDN 链接)

### 6.3 统一数据连接器 (Connectors)
支持 MySQL, PostgreSQL, Doris (SSH Tunnel), Google Sheets。
*   **无需配置 SSH**: 系统自动读取 `~/.ssh/config`。
*   **Pandas Ready**: 查询结果直接返回 DataFrame。

### 6.4 产出与通知 (Outputs & Notifications)
### 6.4 产出与通知 (Outputs & Notifications)
*   **SOM 标准**: 所有产出物自动归档，并生成 `meta.json`。
*   **Domain Router**: 根据业务域 (`marketing`, `risk`) 自动路由通知到不同的 Lark 群组。

> **路由规则 (Routing Rules)**:
> 1.  **L1 Global**: 在 `knowledge/general/config.yaml` 中配置全域路由 (如 `finance.payment` -> Payment Group + Finance Group)。
> 2.  **L3 App**: 在 App `config.yaml` 中配置私有路由 (如 `operations` -> Falcowin Ops Group)。
> 3.  **Broadcast**: 支持多目的地广播，一个事件可同时触达多个飞书群 (One-to-Many)。

### 6.5 Agent Workflows (SOP Engine)
> **设计理念**: Process as Code.

Kiwi 利用 Antigravity 的原生 Workflow 能力，将复杂的 SOP 固化为 Markdown 文件。
*   **路径**: `.agent/workflows/*.md`
*   **作用**: 编排多个 Script，形成完整的业务闭环（如 "每日巡检", "新员工入职"）。
*   **执行**: 只需要对 Agent 说 "Run the daily health check workflow"，它就会按步骤执行。

### 6.6 Agent Skills (Toolbox)
> **设计理念**: Capabilities as Code.

Skill 是 Agent 的**技能包**，赋予它执行复杂任务的“手”。
*   **路径**: `.agent/skills/{skill_name}/`
*   **核心**: 必须包含 `SKILL.md`，告诉 Agent 什么时候用、怎么用这个技能。
*   **示例**: `scaffold_new_script` (代码生成技能)。
*   **机制**: 当你下达指令时，Agent 会检索 Skill 目录，找到匹配的工具并自动调用。

### 6.7 统一服务客户端 (Unified Client SDKs)
> **设计理念**: Write once, reuse everywhere.

*   **路径**: `engine/clients/`
*   **作用**: 封装第三方 API，提供统一的配置注入和错误处理。
*   **可用客户端**:
    *   **`GeminiClient`**: Google AI SDK (v1) 封装，支持多模型切换 (`gemini-2.0-flash`, `gemini-3-pro-preview`)。
    *   **`GoogleSheetClient`**: 基于 `gspread` 的表格读写工具，支持 DataFrame 直接 I/O，自动复用 Service Account 凭证。
    *   **`BaseClient`**: 所有客户端的抽象基类，规范了配置注入接口。

*   **用法示例**:
    ```python
    # 1. AI 分析
    from engine.clients.gemini import GeminiClient
    ai = GeminiClient(self.config, model="gemini-3-pro-preview")
    analysis = ai.generate_content("Analyze this CSV...")

    # 2. 读写 Google Sheet
    from engine.clients.google_sheet import GoogleSheetClient
    gs = GoogleSheetClient() # Auto-Auth
    df = gs.read_as_dataframe("https://docs.google.com/spreadsheets/d/...")
    ```

## 6.8 Google Sheet Configuration
To enable Auto-Reporting to Google Sheets:

1.  **Service Account**: Ensure `secrets/kiwi-*.json` is present and `GOOGLE_APPLICATION_CREDENTIALS` is set.
2.  **Shared Folder (Critical)**: Create a Google Drive Folder and share it with the Service Account Email (Editor Role).
3.  **Config**: Add the `folder_id` to your App Config:
    ```yaml
    delivery:
      google_drive:
        folder_id: "10hgODTfDD4LWQApbqr1-88RZEdmZuuHn" # From Browser URL
        share_with: ["user@company.com"]
    ```
4.  **Workflow**: The script will automatically create Sheets in this folder, bypassing Service Account storage quotas.

---

## 7. 开发规范 (Best Practices)

1.  **强制继承 BaseScript**: 所有业务脚本必须继承 `BaseScript`，以获得参数解析、日志、通知和多租户隔离能力。
2.  **配置解耦**: 敏感信息（密码、Secret）必须使用环境变量 `${ENV_VAR}` 占位，严禁硬编码。
3.  **原子化**: 一个脚本只做一件事 (One Script, One Job)。
4.  **结构化数据**: 优先使用 SQLite (`data/store/.../db/*.db`) 存储中间状态，而非 CSV 文件。
5.  **内核稳定性 (Kernel Stability)**: 
    *   `engine/scripts/core/`, `engine/scripts/utils/`, `engine/clients/` 属于 **系统内核**。
    *   **禁止** 随意修改这些基础类。如果必须修改，必须经过 **人工双重确认 (Human Confirmation)**。

### 7.1 数据处理规范 (Data Processing Standards)
> **原则**: 严禁使用原始的文件读写 (File I/O) 处理业务数据。

1.  **Extract**: 通过 `self.connector.query()` 获取数据，框架会自动返回 DataFrame。
2.  **Transform**: 所有的业务逻辑计算、列重命名、类型转换，**必须** 使用 Pandas DataFrame API。
3.  **Load/Export**: 处理完成后，统一调用 `df.to_csv()` 或 `df.to_excel()` 输出。
4.  **Multi-Output**: 支持单次运行产出多个文件（如 Summary + Details），统一保存至 `output_dir = self.paths.get_output_root(...)`。

### 7.2 依赖管理 (Dependency Management)
项目强制使用 `uv` 进行包管理，严禁使用 `pip install`。

*   **添加依赖**: 
    ```bash
    uv add requests --project engine
    ```
    *   *System*: 自动更新 `engine/pyproject.toml` 和 `engine/uv.lock`。
*   **同步环境**:
    ```bash
    uv sync --project engine
    ```
    *   *CI/CD*: 确保生产环境与开发环境完全一致。
*   **运行脚本**:
    ```bash
    uv run --project engine script.py
    ```

---

---

## 8. 智能分析与自进化 (AI Intelligence)

Kiwi 的终极目标不仅仅是执行脚本，而是成为一个**会思考的运营专家**。
我们设计了 **Lab Mode (实验室模式)** 来支持开放式的数据探索与策略优化。

### 8.1 实验室 (The Lab)
*   **位置**: `workspace/` (Agent 的草稿纸)
*   **能力**: 允许 AI 编写临时 Python 脚本 (`.py` 或 `.ipynb`)，直接调用 Engine 的 `ContextLoader` 和 `Connector` 连接数据库。
*   **场景**: "帮我分析一下为什么昨天 NGR 跌了 30%？" -> AI 会在这里写脚本查数、做相关性分析、出报告。

### 8.2 自进化循环 (Self-Improvement Loop)
针对复杂的**风控策略**或**活动发奖规则**，我们遵循 "Backtest -> Promote" 的流程：

1.  **Exploration (探索)**: AI 在 `workspace/` 中分析历史 30 天数据，训练模型或寻找异常特征（例如：发现 IP 段 `1.2.3.x` 全是套利党）。
2.  **Simulation (回测)**: AI 模拟新规则（"如果当时封了这个段，会误伤多少正常用户？"）。
3.  **Codification (固化)**: 经人工确认后，AI 将规则写入 `knowledge/platforms/.../config.yaml`。
4.  **Execution (执行)**: 生产环境的 Script 读取新 Config，自动生效。

---

*Kiwi Operations Workbench - Powered by Antigravity*
