---
description: 设置 NotebookLLM CLI 工具及其依赖项
---

此工作流将安装 `notebooklm-py` 包及其依赖项（包括 Playwright 浏览器），并引导用户完成登录过程。

1. 安装 Python 包
```bash
uv pip install notebooklm-py
```

2. 安装 Playwright 浏览器 (认证所需)
```bash
uv run playwright install chromium
```

3. 登录 NotebookLLM
> [!IMPORTANT]
> 此步骤是交互式的。将打开一个浏览器窗口。请使用您的 Google 帐户登录。
```bash
# 此命令必须在终端中运行
uv run notebooklm login
```

4. 验证安装
```bash
uv run notebooklm --version
```
