# API 调用示例

## 🚀 快速开始

### 基础认证
所有API请求都需要在Header中携带API密钥：

```bash
Authorization: Bearer your-api-key
```

### 接口基地址
```
https://your-domain/v1
```

## 💬 聊天接口

### Chat Completion

=== "基础调用"
    ```bash
    curl -X POST "https://your-domain/v1/chat/completions" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-3.5-turbo",
        "messages": [
          {"role": "user", "content": "你好"}
        ]
      }'
    ```

=== "流式响应"
    ```javascript
    const response = await fetch('https://your-domain/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer your-api-key',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': '你好'}],
        'stream': true
      })
    });

    const reader = response.body.getReader();
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      console.log(new TextDecoder().decode(value));
    }
    ```

=== "函数调用"
    ```json
    {
      "model": "gpt-3.5-turbo",
      "messages": [{"role": "user", "content": "北京现在几度？"}],
      "functions": [
        {
          "name": "get_weather",
          "description": "获取指定城市的天气信息",
          "parameters": {
            "type": "object",
            "properties": {
              "city": {"type": "string", "description": "城市名称"},
              "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
          }
        }
      ]
    }
    ```

## 🎨 图像生成

### DALL·E

=== "基础生成"
    ```bash
    curl -X POST "https://your-domain/v1/images/generations" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "dall-e-3",
        "prompt": "一只可爱的猫咪",
        "n": 1,
        "size": "1024x1024"
      }'
    ```

=== "高级参数"
    ```json
    {
      "model": "dall-e-3",
      "prompt": "一只可爱的猫咪",
      "n": 1,
      "size": "1024x1024",
      "quality": "hd",
      "style": "natural",
      "response_format": "url"
    }
    ```

### Midjourney

```bash
curl -X POST "https://your-domain/v1/mj/submit" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "a cute cat",
    "action": "IMAGINE"
  }'
```

## 🎵 音频生成

### Suno

```bash
curl -X POST "https://your-domain/v1/audio/generations" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "suno/bark",
    "prompt": "生成一段轻音乐"
  }'
```

## 🔍 文本重排序

### Rerank

=== "Cohere"
    ```bash
    curl -X POST "https://your-domain/v1/rerank" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "rerank-english-v2.0",
        "query": "搜索查询",
        "documents": [
          "文档1",
          "文档2",
          "文档3"
        ]
      }'
    ```

=== "Jina"
    ```bash
    curl -X POST "https://your-domain/v1/rerank" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "jina-rerank-v1-base-en",
        "query": "搜索查询",
        "documents": [
          "文档1",
          "文档2",
          "文档3"
        ]
      }'
    ```

## ⚡ 实时响应

### OpenAI Realtime

```javascript
const ws = new WebSocket('wss://your-domain/v1/chat/completions');
ws.onopen = () => {
  ws.send(JSON.stringify({
    'model': 'gpt-3.5-turbo',
    'messages': [{'role': 'user', 'content': '你好'}]
  }));
};
ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

## 🔧 错误处理

### 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 401 | 未授权 | 检查API密钥是否正确 |
| 429 | 请求过多 | 降低请求频率或增加配额 |
| 500 | 服务器错误 | 尝试重试或联系管理员 |

### 错误响应示例

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "请求频率超过限制",
    "type": "api_error",
    "param": null,
    "status": 429
  }
}
```

## 💡 最佳实践

1. 请求优化
   - 使用流式响应提升体验
   - 合理设置超时时间
   - 实现请求重试机制

2. 错误处理
   - 捕获并处理API错误
   - 实现优雅降级
   - 记录错误日志

3. 性能优化
   - 复用HTTP连接
   - 使用连接池
   - 启用Gzip压缩

4. 安全建议
   - 妥善保管API密钥
   - 使用HTTPS传输
   - 设置请求频率限制 