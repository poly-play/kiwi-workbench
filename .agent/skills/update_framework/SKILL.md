---
name: update_framework
description: 从远程仓库更新 Kiwi 框架代码，同时保留本地个人修改 (Rebase 模式)。
---

# Update Kiwi Framework Skill

此技能用于指导用户或 Agent 如何从远程仓库拉取最新的框架更新 (Kiwi Workbench)，并将本地的个人修改（如配置、私有脚本）应用在最新框架之上。

## 适用场景
*   当 Kiwi 框架发布了新功能或修复了 BUG 时。
*   你需要保持本地工作台是最新版本，但你本地有一些未推送的个人配置或实验性代码。

## 核心原则
1.  **单向流动**: 代码从 Remote -> Local 流动。
2.  **本地保留**: 你的本地修改永远不应被覆盖，而是“浮”在最新框架之上 (Rebase)。
3.  **互不干扰**: 本地修改不需要推送到远程 (Personal Workbench)。

## 操作步骤

### 1. 检查工作区状态 (Status Check)
首先确保工作区干净，避免更新过程中丢失未提交的进度。

```bash
git status
```

*   **如果显示 "clean"**: 继续步骤 2。
*   **如果显示有修改 (modified/untracked)**:
    *   建议先暂存 (Stash) 这些修改，以防万一：
        ```bash
        git stash save "Backup before update"
        ```

### 2. 拉取并变基 (Pull & Rebase)
使用 `rebase` 模式拉取代码。这意味着：“把我的修改暂时拿下来，把远程最新的代码放进去，然后再把我的修改贴回到最上面”。

```bash
git pull --rebase origin main
```

### 3. 处理冲突 (Conflict Resolution)
如果在 Rebase 过程中出现冲突 (`CONFLICT`)，Git 会暂停并提示哪些文件冲突。

#### 处理流程：
1.  **打开冲突文件**: 在编辑器 (VS Code) 中打开提示冲突的文件。
2.  **选择保留内容**:
    *   `Accept Proposed Change` (Incoming): 使用远程的新代码（通常框架核心文件选这个）。
    *   `Accept Current Change` (Current):以此处保留你的本地修改（通常配置或私有逻辑选这个）。
    *   或手动编辑合并。
3.  **标记解决**:
    ```bash
    git add <conflicted_file>
    ```
4.  **继续变基**:
    ```bash
    git rebase --continue
    ```

> **注意**: 如果搞乱了想放弃更新，可以随时运行 `git rebase --abort` 回到更新前的状态。

### 4. 恢复现场 (Pop Stash)
如果在第 1 步执行了 stash，现在需要把刚才暂存的修改拿回来：

```bash
git stash pop
```
*(如果这里又出现冲突，参照第 3 步的方法解决)*

### 5. 验证 (Verify)
更新完成后，简单验证框架是否正常：
```bash
uv run --project engine engine/scripts/tools/verify_environment.py --dry-run
```

## 关键禁令
*   ❌ **禁止运行 `git push`**: 你的本地修改属于个人工作台，不应污染公共远程仓库，除非你明确知道自己在贡献代码。
