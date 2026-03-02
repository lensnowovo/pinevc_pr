# 智谱 AI (GLM) 配置指南

本指南帮助你在 Dify 中配置智谱 AI 的 GLM 系列模型。

## 第一步：获取智谱 AI API Key

### 1. 注册账号

1. 访问 [智谱 AI 开放平台](https://open.bigmodel.cn/)
2. 点击右上角「注册/登录」
3. 使用手机号或微信注册

### 2. 创建 API Key

1. 登录后进入「控制台」
2. 点击左侧菜单「API 密钥管理」
3. 点击「创建 API 密钥」
4. 复制生成的 API Key（格式：`APIKeyID.SecretKey`）

> **重要**：API Key 只显示一次，请立即保存！

### 3. 免费额度

- 新用户有免费调用额度
- GLM-4-Flash 价格：¥0.1/百万 Token（非常便宜）
- 可在控制台查看用量和余额

## 第二步：配置方式

### 方式一：环境变量配置（推荐）

1. 编辑 `deploy/.env` 文件：

```bash
# 智谱 AI API Key
ZHIPUAI_API_KEY=你的APIKeyID.SecretKey
```

2. 重启 Dify 服务：

```bash
# Windows
cd deploy
start.bat restart

# Linux/Mac
cd deploy
./start.sh restart
```

### 方式二：Dify Web 界面配置

1. 访问 http://localhost:3000
2. 登录后点击右上角头像 → 「设置」
3. 选择「模型供应商」
4. 找到「智谱 AI / ZhipuAI」
5. 点击「配置」或「添加」
6. 输入 API Key
7. 点击「保存」

## 第三步：验证配置

### 在 Dify 中测试

1. 进入「工作室」
2. 创建新的应用（聊天助手）
3. 在模型选择中找到「智谱 AI」
4. 选择模型（推荐 `GLM-4-Flash`）
5. 发送测试消息

### 可用模型列表

| 模型 | 说明 | 适用场景 |
|------|------|----------|
| **GLM-4-Flash** | 高性价比 | 日常对话、文本处理（推荐）|
| GLM-4 | 旗舰模型 | 复杂推理、专业任务 |
| GLM-4-Plus | 增强版 | 长文本、代码生成 |
| GLM-4-Long | 长文本 | 文档分析、报告生成 |
| GLM-4V | 多模态 | 图像理解 |

## 常见问题

### Q: API Key 格式错误

确保 API Key 格式正确：`APIKeyID.SecretKey`

例如：`1234567890.abcdefghijklmnopqrst`

### Q: 连接超时

检查网络连接，智谱 AI 服务器在中国大陆，国内访问速度较快。

### Q: 配额不足

登录智谱 AI 控制台查看用量，必要时充值。

### Q: 模型列表为空

1. 确认 API Key 正确
2. 重启 Dify 服务
3. 刷新 Dify 页面

## 价格参考（2026年3月）

| 模型 | 输入价格 | 输出价格 |
|------|----------|----------|
| GLM-4-Flash | ¥0.1/M tokens | ¥0.1/M tokens |
| GLM-4 | ¥50/M tokens | ¥50/M tokens |
| GLM-4-Long | ¥1/M tokens | ¥1/M tokens |

> 价格可能变动，以官网为准

## 相关链接

- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [智谱 AI API 文档](https://open.bigmodel.cn/dev/api)
- [Dify 官方文档](https://docs.dify.ai/)
