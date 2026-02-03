# Git Clone 操作指南 (Windows & Mac) - 运营专用版

本文档旨在指导运营同学如何在 Windows 和 MacOS 环境下安装 Git 并通过 HTTPS 简单快捷地拉取工作台代码。

---

## 1. Windows 环境

### 1.1 安装 Git
1.  下载 **Git for Windows** 安装包: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2.  运行安装程序，**一路保持默认选项**点击 "Next" 直至安装完成。
3.  安装完成后，在任意文件夹右键点击，应能看到 **"Git Bash Here"** 选项。

### 1.2 拉取代码 (Clone)
1.  找到你想存放项目的文件夹 (例如 `D:\Projects`)。
2.  右键 -> **Git Bash Here**。
3.  输入以下命令（复制粘贴并回车）：
    ```bash
    git clone https://github.com/poly-play/kiwi-workbench.git
    ```

### 1.3 身份验证
*   执行上述命令后，如果这是你第一次连接，系统会弹出一个 **"Connect to GitHub"** 的登录窗口。
*   **操作**: 点击 **"Sign in with your browser"** (使用浏览器登录)。
*   在浏览器中授权成功后，下载会自动开始。

---

## 2. MacOS 环境

### 2.1 安装 Git
1.  打开 **Terminal (终端)** (按 `Command + Space`，搜索 Terminal)。
2.  输入 `git --version`。
    *   如果提示安装 **Xcode Command Line Tools**，点击安装并等待完成。
    *   如果有版本号显示，则说明已安装。

### 2.2 配置凭证助手 (推荐)
为了避免频繁输入密码，建议启用凭证助手（大多数 Mac 系统默认已启用，可跳过此步）。

### 2.3 拉取代码 (Clone)
1.  在 Terminal 中输入命令创建目录并进入：
    ```bash
    mkdir -p ~/Projects
    cd ~/Projects
    ```
2.  输入 Clone 命令：
    ```bash
    git clone https://github.com/poly-play/kiwi-workbench.git
    ```

### 2.4 身份验证
*   执行命令后，Terminal 可能会提示输入 `Username` 和 `Password`。
*   **Username**: 输入你的 GitHub 用户名。
*   **Password**: 注意！这里**不能输入登录密码**，必须输入 **Personal Access Token (PAT)**。
    *   *如果不想配置 PAT，建议安装 [GitHub Desktop](https://desktop.github.com/) 客户端进行可视化操作。*

---

## 3. 常见问题 (FAQ)

### Q: Windows 右键没有 "Git Bash Here"?
**A**: 请重新运行安装包，确保在 "Select Components" 步骤勾选了 "Windows Explorer integration"。

### Q: 下载速度很慢或失败 (OpenSSL SSL_read: Connection was reset)?
**A**: 这通常是网络原因。请尝试开启科学上网工具，或者在 Git Bash 中设置代理（咨询技术支持）。

### Q: 如何更新代码？
**A**: 以后需要更新工作台时，只需进入文件夹，右键 Git Bash，输入：
```bash
git pull
```
