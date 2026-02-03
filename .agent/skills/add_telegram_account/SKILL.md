---
description: 添加并授权新的 Telegram 账号用于运营操作。
---

# 添加 Telegram 账号 (Add Telegram Account)

## 1. 技能描述
本技能指导您将一个新的 Telegram 账号接入到系统中。涵盖了交互式认证过程（在手机上接收验证码），以及账号归类（打上特定的角色和区域标签）。

## 2. 前置条件 (Prerequisites)
- **手机号**: 国际格式 (例如: `+1234567890`)。
- **设备访问**: 您需要一台已经登录该账号的设备（手机或电脑），用于接收 2FA 验证码。
- **网络**: 确保运行环境能访问 Telegram 服务器。

## 3. 使用说明 (Usage)

### 命令行 (Command)
```bash
uv run engine/scripts/tools/telegram_auth.py --phone {YOUR_PHONE_NUMBER}
```

### 参数 (Arguments)
- `--phone`: 要添加的账号手机号。

### 交互步骤 (Interactive Steps)
脚本运行后，会提示您输入：
1.  **验证码 (Confirmation Code)**: 发送到您 Telegram App 上的验证码。
2.  **角色 (Role)**: `monitor` (监控视察), `sender` (发消息), 或 `admin` (管理)。
3.  **业务域 (Domain)**: 例如 `operations` (运营), `marketing` (市场)。
4.  **区域 (Region)**: `global` (全球) 或特定国家代码 (如 `br`, `in`)。

## 4. 示例 (Examples)

### 添加一个巴西监控账号
```bash
uv run engine/scripts/tools/telegram_auth.py --phone +5511999999999
# 跟随提示输入: Role=monitor, Domain=operations, Region=br
```

## 5. 故障排除与注意事项 (Troubleshooting)
- **验证**: 运行 `uv run engine/scripts/tools/verify_telegram.py` 可以检查添加后的账号状态。
- **标签修正**: 如果标签打错了，目前需要手动修改数据库或重新运行注册逻辑（如果支持覆盖）。
