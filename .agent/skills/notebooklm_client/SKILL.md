---
name: notebooklm_client
description: 使用 NotebookLLM 来辅助研究、内容生成和分析。
---

# NotebookLLM 客户端 (NotebookLLM Client)

## 1. 技能描述
此技能允许 Antigravity 通过 `notebooklm-py` CLI 与 Google NotebookLLM 进行交互。您可以使用它来创建笔记本、上传文档并生成洞察，实际上相当于为 Agent 扩展了一个临时的、高级的“外脑”。

## 2. 前置条件 (Prerequisites)
- **认证**: 需要有效的 Google 凭证（由 `BaseClient` 处理）。
- **文件**: 有您想要上传的文件的本地路径。

## 3. 使用说明 (Usage)

### 创建与上下文 (Create & Context)
创建一个笔记本并将其设为当前活跃状态。
```bash
uv run notebooklm create "{Topic}"
uv run notebooklm use "{Topic}"
```

### 添加源 (Add Sources)
上传文件到 *活跃* 的笔记本中。
```bash
uv run notebooklm source add "/absolute/path/to/file.md"
```

### 查询/对话 (Query / Chat)
向 *活跃* 的笔记本提问。
```bash
uv run notebooklm ask "{Question}"
```

## 4. 示例 (Examples)

### 生成演示文稿 (Generating a Presentation)
```bash
# 1. 设置
uv run notebooklm create "Kiwi Vision Training"
uv run notebooklm use "Kiwi Vision Training"

# 2. 注入知识
uv run notebooklm source add "/Users/mark/Projects/kiwi/whitepaper.md"

# 3. 生成内容
uv run notebooklm ask "请根据上传的文档，生成一份 10 页的 PPT 大纲。"
```

## 5. 故障排除与注意事项 (Troubleshooting)
- **状态性 (Statefulness)**: CLI 依赖本地状态文件来记录哪个笔记本是“使用中”的。为了安全起见，在开始新会话时，建议总是先运行 `use`，然后再运行 `source add` 或 `ask`。
- **配额**: 大文件可能会触发 NotebookLLM 的上传限制。
