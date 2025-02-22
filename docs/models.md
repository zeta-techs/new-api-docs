# 🎯 模型支持

## 💫 支持的模型类型

### OpenAI 系列

| 模型 | 说明 | 特点 | 适用场景 |
|------|------|------|----------|
| `gpt-4-turbo` | GPT-4最新版本 | 更强大的理解和生成能力 | 复杂任务处理 |
| `gpt-4` | GPT-4基础版本 | 强大的推理能力 | 高质量内容生成 |
| `gpt-3.5-turbo` | GPT-3.5增强版 | 快速响应，性价比高 | 日常对话和任务 |
| `gpt-4-gizmo-*` | GPT-4 Gizmo | 第三方模型，特殊功能 | 定制化需求 |
| `dall-e-3` | 最新图像生成模型 | 高质量，细节丰富 | 专业图像创作 |
| `dall-e-2` | 基础图像生成模型 | 速度快，成本低 | 简单图像生成 |
| `whisper` | 语音识别模型 | 多语言支持 | 音频转文字 |

### Anthropic 系列

| 模型 | 说明 | 特点 |
|------|------|------|
| `claude-3-opus` | Claude 3最强版本 | 超强理解和生成能力 |
| `claude-3-sonnet` | Claude 3标准版 | 平衡性能和效率 |
| `claude-3-haiku` | Claude 3轻量版 | 快速响应，低成本 |
| `claude-2.1` | Claude 2.1版本 | 稳定可靠 |

### Google 系列

| 模型 | 说明 | 特点 |
|------|------|------|
| `gemini-pro` | Gemini专业版 | 强大的多模态能力 |
| `gemini-pro-vision` | Gemini视觉版 | 图像理解和分析 |

### 图像生成

| 模型 | 说明 | 特点 |
|------|------|------|
| `midjourney` | MJ图像生成 | 艺术风格强 |
| `stable-diffusion` | SD开源模型 | 可本地部署 |
| `dall-e` | OpenAI模型 | 真实感强 |

### 音频生成

| 模型 | 说明 | 特点 |
|------|------|------|
| `suno/bark` | 语音合成 | 多语言支持 |
| `suno/musicgen` | 音乐生成 | 多风格支持 |

### 自定义渠道

!!! tip "自定义渠道支持"
    在渠道编辑中可以设置完整的API调用地址，支持：
    - 私有部署的模型服务
    - 第三方兼容接口
    - 自定义的API网关

### Dify 支持

| 功能 | 说明 | 配置 |
|------|------|------|
| 工作流调试 | 输出工作流和节点信息 | `DIFY_DEBUG=true` |
| API集成 | 支持标准API调用 | 配置渠道类型为 `dify` |
| 应用接入 | 支持应用级别接入 | 设置应用ID和密钥 |

## 🎛️ 高级特性

### Reasoning Effort 设置

通过模型名称后缀可以控制模型的推理深度：

| 后缀 | 效果 | 示例 |
|------|------|------|
| `-high` | 高强度推理 | `o3-mini-high` |
| `-medium` | 中等推理 | `o3-mini-medium` |
| `-low` | 低强度推理 | `o3-mini-low` |

### 模型版本控制

```bash
# Gemini 模型版本指定
GEMINI_MODEL_MAP="gemini-1.5-pro-latest:v1beta,gemini-1.5-pro-001:v1beta"
```

## 💡 使用建议

1. 模型选择
   - 日常对话：使用 `gpt-3.5-turbo`
   - 复杂任务：使用 `gpt-4` 或 `claude-3`
   - 图像生成：使用 `dall-e-3` 或 `midjourney`
   - 特殊需求：使用 `gpt-4-gizmo-*` 或自定义模型

2. 性能优化
   - 合理设置 reasoning effort
   - 选择适合的模型版本
   - 使用模型组合提升效果

3. 成本控制
   - 根据任务复杂度选择模型
   - 合理设置 token 限制
   - 使用缓存减少调用

!!! tip "模型使用提示"
    1. `gpt-4-gizmo-*` 为第三方模型，使用官方key无法调用
    2. 自定义渠道需要确保API格式兼容
    3. 合理设置 reasoning effort 可以优化输出质量
    4. 定期评估模型性能和成本

## ⚙️ 模型配置

### 基础配置

```json
{
  "model": "模型名称",
  "params": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000,
    "presence_penalty": 0,
    "frequency_penalty": 0
  }
}
```

### 高级参数

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `temperature` | 随机性 | `0.7` | `0-2` |
| `top_p` | 采样阈值 | `0.9` | `0-1` |
| `max_tokens` | 最大生成长度 | `2000` | 模型相关 |
| `presence_penalty` | 主题新鲜度 | `0` | `-2-2` |
| `frequency_penalty` | 词频惩罚度 | `0` | `-2-2` |

## 🔄 模型调用

### 基础调用

```bash
curl -X POST "https://your-domain/v1/chat/completions" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### 流式调用

```javascript
const response = await fetch('/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-3.5-turbo',
    messages: [{role: 'user', content: 'Hello!'}],
    stream: true
  })
});

const reader = response.body.getReader();
while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  console.log(new TextDecoder().decode(value));
}
```

## 🔍 故障排查

### 常见问题

1. 响应超时
   - 检查模型负载
   - 调整超时设置
   - 使用流式响应

2. 生成质量
   - 优化提示词
   - 调整温度参数
   - 选择合适模型

3. 成本控制
   - 设置令牌限制
   - 使用缓存机制
   - 选择经济型模型

### 监控指标

```yaml
monitoring:
  latency:
    p95: 2000ms
    p99: 5000ms
  success_rate: 99.5%
  token_usage:
    prompt: 1000
    completion: 2000
  cost_per_request: $0.02
```

!!! tip "使用建议"
    1. 根据任务选择合适的模型
    2. 优化提示词和参数配置
    3. 实现合理的错误处理
    4. 监控使用量和成本
    5. 定期评估和优化 