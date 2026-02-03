# 🔑 如何获取 Google Gemini API Key

Kiwi 的智能化能力（AI 分析、写代码、写 SQL）完全依赖于 Google Gemini 模型。
你需要申请一个免费的 API Key 才能启动它。

## 步骤 (无需绑卡)

1.  **访问 Google AI Studio**:
    *   点击链接: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    *   *(需要登录 Google 账号)*

2.  **创建密钥**:
    *   点击页面上的蓝色大按钮 **"Create API key"**。
    *   如果为了测试，可以选择 "Create API key in new project"。

3.  **复制密钥**:
    *   你会看到一串以 `AIza` 开头的长字符串。
    *   点击复制按钮。

4.  **配置 Kiwi**:
    *   回到 Kiwi 项目目录。
    *   打开 `.env` 文件。
    *   找到 `GEMINI_API_KEY=` 这一行。
    *   粘贴你的密钥：`GEMINI_API_KEY=AIzaSyDxxxxxxxxx`
    *   保存文件。

---

> **注意**: 这个 Key 是免费的，但请不要分享给其他人。
