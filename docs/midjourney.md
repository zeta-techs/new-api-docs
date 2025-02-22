# Midjourney 接入指南

## 🚀 快速开始

### 前置要求

!!! note "准备工作"
    1. 已部署 [Midjourney-Proxy(Plus)](https://github.com/novicezk/midjourney-proxy) 服务
    2. 已获取 Midjourney-Proxy 的 API 密钥
    3. 确保 Midjourney-Proxy 服务可正常访问

### 添加渠道

1. 进入管理后台 -> 渠道管理
2. 点击"新建渠道"
3. 选择类型为 `Midjourney`
4. 填写配置信息：

```json
{
  "name": "MJ渠道",
  "type": "midjourney",
  "key": "your-mj-proxy-key",
  "base_url": "http://your-mj-proxy-host:port",
  "weight": 100,
  "models": ["midjourney/*"]
}
```

## 💫 功能支持

### 支持的模型

| 模型名称 | 说明 | 示例 |
|---------|------|------|
| `midjourney/imagine` | 文生图 | 根据文本生成图片 |
| `midjourney/upscale` | 放大图片 | 放大选定的图片变体 |
| `midjourney/variation` | 变体图片 | 生成选定图片的变体 |
| `midjourney/describe` | 图生文 | 分析图片生成提示词 |
| `midjourney/blend` | 图片混合 | 混合多张图片 |
| `midjourney/reroll` | 重新生成 | 使用相同参数重新生成 |
| `midjourney/action` | 自定义操作 | 执行自定义动作 |

## 📝 API 示例

### 文生图 (Imagine)

=== "基础请求"
    ```bash
    curl -X POST "https://your-domain/v1/mj/submit" \
      -H "Authorization: Bearer your-api-key" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "midjourney/imagine",
        "prompt": "a cute cat",
        "action": "IMAGINE"
      }'
    ```

=== "高级参数"
    ```json
    {
      "model": "midjourney/imagine",
      "prompt": "a cute cat",
      "action": "IMAGINE",
      "params": {
        "aspect_ratio": "1:1",
        "quality": "1",
        "style": "raw",
        "version": "6"
      }
    }
    ```

### 图片操作

=== "放大"
    ```json
    {
      "model": "midjourney/upscale",
      "task_id": "已有任务ID",
      "index": 1,
      "action": "UPSCALE"
    }
    ```

=== "变体"
    ```json
    {
      "model": "midjourney/variation",
      "task_id": "已有任务ID",
      "index": 1,
      "action": "VARIATION"
    }
    ```

=== "混合"
    ```json
    {
      "model": "midjourney/blend",
      "images": [
        "base64_image_1",
        "base64_image_2"
      ],
      "action": "BLEND"
    }
    ```

## 🔄 任务状态

### 状态说明

| 状态 | 说明 | 处理建议 |
|------|------|----------|
| `PENDING` | 等待处理 | 继续轮询 |
| `RUNNING` | 正在执行 | 继续轮询 |
| `SUCCESS` | 执行成功 | 获取结果 |
| `FAILURE` | 执行失败 | 查看错误信息 |

### 查询任务

```bash
curl -X GET "https://your-domain/v1/mj/task/{task_id}" \
  -H "Authorization: Bearer your-api-key"
```

## ⚙️ 高级配置

### 参数说明

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `aspect_ratio` | 图片比例 | `1:1` | `1:1`, `16:9`, `4:3` |
| `quality` | 图片质量 | `1` | `0.25`, `0.5`, `1` |
| `style` | 生成风格 | `raw` | `raw`, `cute`, `expressive` |
| `version` | MJ版本 | `6` | `5.2`, `6`, `niji` |

### 自定义操作

```json
{
  "model": "midjourney/action",
  "action": "CUSTOM",
  "params": {
    "command": "自定义命令",
    "options": {
      "key": "value"
    }
  }
}
```

## 🔍 故障排查

### 常见问题

1. 连接超时
   - 检查 Proxy 服务是否可访问
   - 确认网络连接正常
   - 适当增加超时时间

2. 任务失败
   - 验证 API 密钥是否正确
   - 检查 Discord 服务状态
   - 查看详细错误信息

3. 图片生成失败
   - 确认提示词格式正确
   - 检查参数是否有效
   - 验证账户额度充足

### 错误处理

```javascript
try {
  const response = await fetch('/v1/mj/submit', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'midjourney/imagine',
      prompt: 'a cute cat'
    })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error);
    // 处理错误...
  }
} catch (err) {
  console.error('Request failed:', err);
  // 处理异常...
}
```

## 💡 最佳实践

1. 提示词优化
   - 使用清晰的描述
   - 添加适当的风格词
   - 控制提示词长度

2. 性能优化
   - 合理设置轮询间隔
   - 使用 WebSocket 接收更新
   - 实现请求缓存

3. 错误处理
   - 实现请求重试
   - 添加超时处理
   - 记录详细日志

4. 资源管理
   - 监控任务状态
   - 清理过期任务
   - 控制并发请求 