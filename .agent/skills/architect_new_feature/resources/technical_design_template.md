# [Feature Name] 技术方案设计文档 (TDD) v4.0

## 1. 架构定义 (Architecture Definition)

### 1.1 组件定位
*   **Role**: [Script / Workflow / Reporter / Sensor / Connector / Client / Driver / Cron Job]
*   **Implementation Pattern**: [Choose One from Below: A / B / C / D]

---

## 2. 详细设计 (Pattern Implementation)
*(Fill ONLY the section relevant to your Implementation Pattern)*

### Pattern A: 业务逻辑脚本 (Script / Workflow / Sensor)
*   **Path**: `engine/scripts/[domain]/.../[name].py`
*   **Data Strategy**:
    *   **Source**: [DorisClient / API]
    *   **State**: [None / SQLite DB `data/store/...`]
    *   **Output**: [Generate CSV / Slack Msg]
*   **Logic Flow**:
    1.  **Extract**: Use `self.connector` or `Client`.
    2.  **Transform**: Use **Pandas** (Strict Requirement).
    3.  **Load**: Write to `data/outputs/`.

### Pattern B: 任务调度 (Cron Job)
*   **Registry**: `knowledge/scheduler.yaml`
*   **Job Definition**:
    ```yaml
    - name: [job_name]
      schedule: "0 8 * * *"  # [Crontab Expression]
      command: "uv run engine/scripts/..."
      args:
        - "--app"
        - "{app}"
      apps: ["jeetup", "saker"] # Matrix Execution
      lock: "skip" # [skip / block / allow]
    ```

### Pattern C: 通用报表 (Generic Reporter)
*   **Config Path**: `knowledge/reports/[domain]/[report_name].yaml`
*   **Definition**:
    ```yaml
    query: |
      SELECT date, user_id, amount 
      FROM payment_table 
      WHERE date = '{yesterday}'
    columns: ["日期", "用户", "金额"]
    alert_rules:
      - condition: "amount > 10000"
        level: "critical"
    notify:
      channels: ["finance_group"]
    ```

### Pattern D: 基础设施 (Connector / Client / Driver)
*   **Parent Class**: [`BaseClient` / `BaseDriver`]
*   **Config Path**: `config.yaml` at `[Global / Region / App]` level.
*   **Auth Method**:
    *   [ ] Use `.env` (Global Secrets)
    *   [ ] Use `secrets/xxx.json` (File Secrets)

---

## 3. 配置与注册 (Configuration & Registry)

### 3.1 逻辑配置 (Config)
*   **Scope**: [L1 Global / L2 Region / L3 App]
*   **Location**: `knowledge/[path]/config.yaml`

### 3.2 密钥管理 (Secrets)
*   **Type**: [Global .env / App .env]
*   **Warning**: 严禁硬编码。

### 3.3 系统注册 (Registry)
*   **Script Library**: 是否需要注册到 `knowledge/script_library.yaml` 以供 AI 发现？
    *   [ ] Yes (Name: `[skill_name]`)
    *   [ ] No (Internal only)

---

## 4. 验证计划 (Verification Plan)

### 4.1 Dry Run (Simulation)
*   Command: `uv run ... --dry-run`
*   Expected: Show logic log, NO write actions.

### 4.2 Real Execution
*   Target App: [test_app / br_ops]

### 4.3 Edge Cases
*   [ ] Data Empty
*   [ ] Network Timeout

---

## 5. 完工审计 (Post-Implementation Audit)
*To be checked by Agent BEFORE marking task as complete.*

- [ ] **Code Standards**:
    - [ ] Inherits `BaseScript` (or `BaseClient`).
    - [ ] Uses `Pandas` for data transformation.
    - [ ] No hardcoded paths (uses `self.paths`).
- **Data Integrity**:
    - [ ] Output files are in `data/outputs`.
    - [ ] Intermediate DB is in `data/store`.
- **Documentation**:
    - [ ] `SKILL.md` (if new skill).
    - [ ] `SKILL.md` (if new skill).
    - [ ] Requirements Requirements (`requirements_*.md`) are met.
- **Compliance Check**:
    - [ ] **Data Taxonomy**: Does it respect `Knowledge` vs `Store` vs `Output` as defined in `README.md`?
    - [ ] **Multi-Tenancy**: Does it support `python script.py --app {app}`?
    - [ ] **Zero File I/O for Data**: Does it use Pandas for all business logic?
