# OpenAI 格式聊天接口

## 🔑 认证说明

所有API请求都需要在Header中携带API密钥：

```bash
Authorization: Bearer your-api-key
```

接口基地址:
```
https://api2.aigcbest.top/v1
```

## 💬 接口类型

所有接口均已适配 v1/chat/completions 格式,只需要把模型名称完整复制到model参数即可使用。

### 1. 聊天接口 (Chat Completions)

**请求地址:** POST https://api2.aigcbest.top/v1/chat/completions

**功能说明:** 基础的文本对话接口,支持各类模型的对话交互。

=== "基础调用"
    ```bash
    curl -X POST "https://api2.aigcbest.top/v1/chat/completions" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o",
        "messages": [
          {"role": "user", "content": "你好"}
        ]
      }'
    ```

=== "流式响应"
    ```javascript
    const response = await fetch('https://api2.aigcbest.top/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer your-api-key',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        'model': 'gpt-4o',
        'messages': [{'role': 'user', 'content': '你好'}],
        'stream': true
      })
    });
    ```

### 2. 识图接口

**请求地址:** POST https://api2.aigcbest.top/v1/chat/completions

**功能说明:** 支持图片理解和分析的多模态对话接口。图片需要以URL形式传入。

=== "图片分析"
    ```json
    {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user", 
          "content": [
            {
              "type": "text",
              "text": "这张图片是什么?"
            },
            {
              "type": "image_url",
              "image_url": {
                "url": "图片URL"
              }
            }
          ]
        }
      ]
    }
    ```

=== "完整示例"
    ```bash
    curl -X POST "https://api2.aigcbest.top/v1/chat/completions" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": "描述这张图片"
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": "https://example.com/image.jpg"
                }
              }
            ]
          }
        ]
      }'
    ```

### 3. Function Calling

**请求地址:** POST https://api2.aigcbest.top/v1/chat/completions

**功能说明:** 支持函数调用的结构化对话接口,可以让模型调用预定义的函数。

=== "天气查询示例"
    ```json
    {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "user",
          "content": "北京今天天气怎么样"
        }
      ],
      "tools": [
        {
          "type": "function",
          "function": {
            "name": "get_current_weather",
            "description": "获取指定位置的当前天气",
            "parameters": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "description": "城市名称"
                },
                "unit": {
                  "type": "string",
                  "enum": ["celsius", "fahrenheit"]
                }
              },
              "required": ["location"]
            }
          }
        }
      ]
    }
    ```

=== "完整调用"
    ```bash
    curl -X POST "https://api2.aigcbest.top/v1/chat/completions" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "北京今天天气怎么样"}],
        "tools": [{
          "type": "function",
          "function": {
            "name": "get_current_weather",
            "description": "获取天气信息",
            "parameters": {
              "type": "object",
              "properties": {
                "location": {"type": "string", "description": "城市名称"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
              },
              "required": ["location"]
            }
          }
        }]
      }'
    ```

### 4. JSON Schema 结构化输出

**请求地址:** POST https://api2.aigcbest.top/v1/chat/completions

**功能说明:** 支持通过JSON Schema定义输出格式的结构化响应接口。

=== "数学解答示例"
    ```json
    {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "system",
          "content": "你是一个数学老师"
        },
        {
          "role": "user",
          "content": "求解方程: 8x + 31 = 2"
        }
      ],
      "response_format": {
        "type": "json_schema",
        "json_schema": {
          "type": "object",
          "properties": {
            "steps": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "explanation": {"type": "string"},
                  "output": {"type": "string"}
                }
              }
            },
            "final_answer": {"type": "string"}
          }
        }
      }
    }
    ```

=== "完整调用"
    ```bash
    curl -X POST "https://api2.aigcbest.top/v1/chat/completions" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o",
        "messages": [
          {"role": "user", "content": "求解方程: 8x + 31 = 2"}
        ],
        "response_format": {
          "type": "json_schema",
          "json_schema": {
            "type": "object",
            "properties": {
              "steps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "explanation": {"type": "string"},
                    "output": {"type": "string"}
                  }
                }
              },
              "final_answer": {"type": "string"}
            }
          }
        }
      }'
    ```

## 📝 通用参数说明

### Header 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| Content-Type | string | 是 | application/json |
| Accept | string | 是 | application/json |
| Authorization | string | 是 | Bearer your-api-key |

### Body 参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| model | string | 是 | 使用的模型ID |
| messages | array | 是 | 对话消息数组 |
| temperature | number | 否 | 采样温度(0-2) |
| max_tokens | integer | 否 | 最大生成token数 |
| stream | boolean | 否 | 是否启用流式响应 |
| presence_penalty | number | 否 | -2.0到2.0,控制主题新颖度 |
| frequency_penalty | number | 否 | -2.0到2.0,控制重复度 |
| top_p | number | 否 | 核采样概率(0-1) |
| n | integer | 否 | 生成回复数量 |
| stop | string/array | 否 | 停止生成的标记 |
| logit_bias | object | 否 | token生成概率偏置 |
| user | string | 否 | 用户标识符 |

### messages 参数说明

| 字段 | 类型 | 说明 |
|------|------|------|
| role | string | 消息角色(system/user/assistant) |
| content | string/array | 消息内容,支持文本或多模态数组 |
| name | string | 可选,消息发送者名称 |

## ⚡ 响应格式

所有接口统一返回以下格式:

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "响应内容"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 9,
    "completion_tokens": 12,
    "total_tokens": 21
  }
}
```

### 响应参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | string | 响应ID |
| object | string | 响应类型 |
| created | integer | 创建时间戳 |
| choices | array | 响应内容数组 |
| usage | object | token使用统计 |
| finish_reason | string | 结束原因(stop/length/content_filter) |

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |