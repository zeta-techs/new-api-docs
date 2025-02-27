# New API 快速调用指南

本文档提供常见的 New API 调用方法和示例，帮助您快速接入和使用 API。

## 前提条件

- 已成功部署 New API 服务
- 已创建可用的 API 令牌（Token）

## 基本调用格式

New API 兼容 OpenAI API 格式，基本调用地址为：

```
http(s)://your-server-address[:port]/v1/...
```

所有请求都需要在 Header 中添加授权信息：

```
Authorization: Bearer your-token-here
```

## 常用 API 调用示例

### 1. 聊天补全 (Chat Completions)

```bash
curl http://your-server-address:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "system", "content": "你是一个有用的助手。"},
      {"role": "user", "content": "请介绍一下自己。"}
    ],
    "temperature": 0.7
  }'
```

### 2. 流式输出 (Streaming)

```bash
curl http://your-server-address:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "写一首关于人工智能的诗"}],
    "stream": true
  }'
```

### 3. 图像生成 (Image Generation)

```bash
curl http://your-server-address:3000/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "dall-e-3",
    "prompt": "一只可爱的猫咪在玩电脑",
    "n": 1,
    "size": "1024x1024"
  }'
```

### 4. 使用 Midjourney

```bash
curl http://your-server-address:3000/mj/submit/imagine \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "prompt": "一只宇航员猫咪在太空站",
    "base64": false
  }'
```

### 5. 使用 Suno 生成音乐

```bash
curl http://your-server-address:3000/v1/audio/speech \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "suno-bark",
    "input": "让我们一起唱一首歌",
    "voice": "female"
  }'
```

### 6. 查询模型列表

```bash
curl http://your-server-address:3000/v1/models \
  -H "Authorization: Bearer your-token"
```

### 7. 查询令牌余额

```bash
curl http://your-server-address:3000/v1/dashboard/billing/subscription \
  -H "Authorization: Bearer your-token"
```

## 使用特定功能

### 高级参数

您可以使用以下高级参数定制模型行为：

- `temperature`: 控制随机性 (0-2)
- `top_p`: 控制生成的多样性 (0-1)
- `presence_penalty`: 重复惩罚系数 (-2.0-2.0)
- `frequency_penalty`: 频率惩罚系数 (-2.0-2.0)
- `max_tokens`: 最大生成令牌数

### 模型后缀使用

通过附加特定后缀修改模型行为：

- OpenAI o系列模型: `-high`, `-medium`, `-low` (如 `o3-mini-high`)
- Claude 思考模式: `-thinking` (如 `claude-3-7-sonnet-20250219-thinking`)

## 错误处理

常见错误码及处理方法：

- `401`: 令牌无效或已过期
- `402`: 账户余额不足
- `429`: 请求过于频繁，需要减缓请求速率
- `500`: 服务器内部错误，可尝试重新请求

## 库和SDK

推荐使用以下第三方库简化调用：

- Python: `openai-python`
- JavaScript: `openai-node`
- PHP: `openai-php`

## 更多资源

- [完整API文档](../api-docs/introduction.md)
- [模型支持列表](../user-guide/supported-models.md)
- [高级配置](../user-guide/advanced-configuration.md)
