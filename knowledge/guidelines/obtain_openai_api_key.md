# 如何获取 OpenAI API Key

如果您需要使用 OpenAI 的服务 (如 GPT-4)，您需要获取一个 API Key。

## 1. 注册/登录 OpenAI 账号
访问 [OpenAI Platform](https://platform.openai.com/) 并使用您的邮箱注册或登录。

## 2. 绑定支付方式 (必要步骤)
OpenAI 的 API 需要绑定信用卡才能使用 (即使有免费额度通常也需要验证)。
1. 点击左侧菜单的 **Settings** -> **Billing**。
2. 点击 **Add payment details** 绑定您的国际信用卡 (Visa/Mastercard)。
    * *注意: 国内信用卡通常无法直接使用，可能需要使用虚拟卡或海外卡。*
3. 建议设置 **Usage limits** (用量上限)，防止费用超支。

## 3. 创建 API Key
1. 点击左侧菜单的 **API Keys** (或者直接访问 [API Keys 页面](https://platform.openai.com/api-keys))。
2. 点击 **Create new secret key** 按钮。
3. **Name**: (可选) 为 Key 起个名字，例如 "Kiwi Workbench"。
4. **Permissions**: 通常选择 "All" 即可。
5. 点击 **Create secret key**。

## 4. 保存 Key
**重要**: Key 只会显示一次！
*   请立即复制以 `sk-...` 开头的字符串。
*   将其保存在安全的地方 (例如密码管理器)。
*   如果您丢失了 Key，只能删除并重新创建一个新的。

## 5. 在工作台中使用
将 Key 配置到您的环境变量文件 (`.env`) 中：

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```
