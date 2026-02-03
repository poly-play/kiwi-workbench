# Google Drive Connector Setup Guide (Google Drive 接入指南)

> **适用对象**: 运维团队 / 开发者 / 这里需要连接自己 Google Drive 的任何人。
> **目的**: 允许 Kiwi 机器人以**你的身份**上传文件到你的 Google Drive (使用你的 15GB+ 存储空间)。

---

## 🛑 为什么要这样做? (Why?)
Google 的 **Service Account (机器人账号)** 默认是 **0 存储空间** 的。它不能把文件上传到它自己的空间，也无法向你个人的 Google Drive 文件夹上传文件（除非你是 Google Workspace 付费企业版管理员并配置了域权限）。

因此，最稳定、最简单的方案是：**让机器人获得你的“授权许可” (OAuth Token)**，让它代表你去上传文件。

---

## ✅ 步骤一：创建凭证 (Create Credentials)
*(只需要做一次)*

1.  打开 **[Google Cloud Console](https://console.cloud.google.com/apis/credentials)**。
2.  确保顶部的项目 (Project) 是 **`kiwi-485709`** (或其他你也正在使用的 Kiwi 项目)。
3.  点击 **"+ CREATE CREDENTIALS"** -> 选择 **"OAuth client ID"**。
4.  **Application type** 选择: **Desktop app** (桌面应用)。
5.  **Name** 填: `Kiwi Drive uploader` (或者随意)。
6.  点击 **Create**。
7.  在弹出的窗口中，点击 **DOWNLOAD JSON** (下载图标)。
8.  **重命名** 下载的文件为 `client_secret.json`。
9.  将该文件放入项目的 `secrets/` 文件夹中：
    *   路径: `igaming-operation/secrets/client_secret.json`

---

## ✅ 步骤二：一键登录 (Login)
*(只需要做一次，或者当 Token 过期时)*

1.  在终端 (Terminal) 中运行以下命令：
    ```bash
    uv run --project engine engine/scripts/setup/google_auth.py
    ```

2.  脚本会自动打开浏览器，或者给你一个链接。
3.  登录你的 Google 账号。
4.  Google 会提示 "Kiwi wants to access your Google Account"。
    *   勾选/同意 **Access Google Drive files** 权限。
    *   点击 **Continue/Allow**。
5.  回到终端，你会看到：`✅ Authentication successful! Token saved...`

---

## ✅ 步骤三：验证 (Verify)

现在所有配置都完成了！Kiwi 现在拥有了上传文件的能力。

*   **凭证位置**: `secrets/google_drive_token.json` (这是你的数字钥匙，请勿分享)
*   **如何撤销**: 你随时可以在 [Google Account Permissions](https://myaccount.google.com/permissions) 中移除 Kiwi 的权限。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么显示 "App not verified"?**
A: 因为这是咱们内部自己创建的测试 App，Google 还没审核。点击左下角的 **"Advanced" (高级)** -> **"Go to ... (unsafe)"** 即可。这是安全的，因为你自己就是 App 的开发者。

**Q: 为什么显示 "Access blocked: kiwi ai has not completed the Google verification process" (Error 403)?**
A: 这是因为 App 处于 **Testing** 模式，且你的邮箱不在白名单里。
**解决方法**:
1.  进入 **[Google Cloud Console > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**。
2.  滚动到 **Test users** 区域。
3.  点击 **+ ADD USERS**，添加你的邮箱 (例如 `marklee2037@gmail.com`)。
4.  保存后，重新运行脚本即可。

**Q: Token 会过期吗?**
A: 是的。如果脚本报错 "Token expired" 或 "Auth failed"，请重新运行 **步骤二** 即可。
