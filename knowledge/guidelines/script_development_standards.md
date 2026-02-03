# Engine Script Development Standards

> **Version**: 1.0
> **Scope**: All Python scripts under `engine/scripts/`
> **Audience**: AI Agents & Human Developers

This document defines the strict coding standards for the Kiwi Operations Engine. **All new scripts MUST adhere to these rules.**

---

## 1. Core Architecture

### 1.1 Inheritance
All scripts **MUST** inherit from `BaseScript` to ensure consistent logging, configuration, and args parsing.

```python
# ✅ CORRECT
from engine.scripts.core.base_script import BaseScript

class MyScript(BaseScript):
    def run(self, args):
        ...

# ❌ INCORRECT
class MyScript:
    def run(self):
        ...
```

### 1.2 Entry Point
Scripts must use the standard execution pattern:

```python
if __name__ == "__main__":
    MyScript().execute()
```

---

## 2. Configuration & State

### 2.1 Config Access
Do **NOT** load `.env` or `yaml` files manually. The `BaseScript` automatically loads the merged context (Global > Region > App > Env) into `self.config`.

```python
# ✅ CORRECT
db_host = self.config.get("datasources", {}).get("doris", {}).get("host")

# ❌ INCORRECT
import os
db_host = os.getenv("DORIS_HOST") # Unless it's a raw secret override
```

### 2.2 Secrets
**NEVER** hardcode secrets. Use environment variables loaded by the framework.

```python
# ✅ CORRECT
password = os.environ.get("DB_PASSWORD")

# ❌ INCORRECT
password = "my_secret_password"
```

---

## 3. Data Handling

### 3.1 Connector Pattern
Use the Unified Client SDKs or Connectors. Do not create raw connections (e.g. `pymysql.connect`) unless writing a new connector.

```python
# ✅ CORRECT
from engine.clients.google_sheet import GoogleSheetClient
gs = GoogleSheetClient()

# ❌ INCORRECT
import gspread
gc = gspread.service_account(...)
```

### 3.2 Pandas-First
For operational data processing, use Pandas DataFrames.

*   **Extract**: `df = client.read_as_dataframe(...)`
*   **Transform**: `df['roi'] = df['revenue'] / df['cost']`
*   **Load**: `df.to_csv(...)`

---

## 4. File System & Paths

Do NOT use relative paths like `../../data`. Use the `self.paths` helper (from `engine.scripts.utils.paths`).

*   **Store (Persistent)**: `self.paths.get_store_path("domain", "app", "file.json")`
*   **Output (Artifacts)**: `self.paths.get_output_path(...)`
*   **Temp**: `self.paths.get_tmp_path(...)`

```python
# ✅ CORRECT
out_file = self.paths.get_output_path(self.domain, self.config['app_name'], "report.csv")
df.to_csv(out_file)
```

---

## 5. Logging & Output

### 5.1 Logging
Use `self.logger`. Do not use `print()` for process status (exceptions: CLI tools where output is pipe-able).

```python
# ✅ CORRECT
self.logger.info(f"Processing {len(df)} records...")
self.logger.error("Connection failed")

# ❌ INCORRECT
print("Starting...")
```

### 5.2 Notifications
Use `self.notifier` for business alerts.

```python
self.notifier.send(
    title="Daily Report",
    text=summary_text,
    link=sheet_url
)
```

---

## 6. Type Hinting
All methods signatures **MUST** be typed.

```python
def calculate_roi(self, spend: float, revenue: float) -> float:
    if spend == 0: return 0.0
    return revenue / spend
```

---

## 7. Example Template

```python
from engine.scripts.core.base_script import BaseScript
import pandas as pd

class ExampleScript(BaseScript):
    def run(self, args):
        self.logger.info("Starting Example Script")
        
        # 1. Config
        target_roi = self.config.get("marketing", {}).get("target_roi", 1.5)
        
        # 2. Logic
        # ... calculation ...
        
        # 3. Output
        self.logger.info("Done")

if __name__ == "__main__":
    ExampleScript().execute()
```
