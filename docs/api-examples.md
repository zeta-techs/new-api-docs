# API 调用示例

## 基础调用

### 聊天补全 (Chat Completion)
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

### 图像生成 (DALL·E)
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

## 高级功能

### 流式响应
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
  // 处理流式数据
}
```

### 函数调用
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

## 错误处理

常见错误码及处理方法：

| 错误码 | 说明 | 处理方法 |
|--------|------|----------|
| 401 | 未授权 | 检查API密钥是否正确 |
| 429 | 请求过多 | 降低请求频率或增加配额 |
| 500 | 服务器错误 | 尝试重试或联系管理员 |

## 最佳实践

1. 设置合理的超时时间
2. 实现请求重试机制
3. 使用流式响应提升体验
4. 合理设置模型参数
5. 做好错误处理 