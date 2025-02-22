# Midjourney 接入指南

## 前置要求

1. 已部署 [Midjourney-Proxy(Plus)](https://github.com/novicezk/midjourney-proxy) 服务
2. 已获取 Midjourney-Proxy 的 API 密钥

## 配置步骤

### 1. 添加渠道
在 New API 管理后台:

1. 进入`渠道管理`
2. 点击`新建渠道`
3. 选择类型为`Midjourney`
4. 填写以下信息:
   - 名称: 自定义渠道名称
   - 密钥: Midjourney-Proxy 的 API 密钥
   - 基础地址: Midjourney-Proxy 服务地址
   - 其他选项可按需配置

### 2. 支持的模型
添加渠道后,系统会自动创建以下模型:

- `midjourney/imagine`: 生成图片
- `midjourney/upscale`: 放大图片
- `midjourney/variation`: 变体图片
- `midjourney/describe`: 图生文
- `midjourney/blend`: 图片混合
- `midjourney/reroll`: 重新生成
- `midjourney/action`: 自定义操作

## 调用示例

### 文生图(Imagine)
```json
{
    "model": "midjourney/imagine",
    "prompt": "A cute cat"
}
```

### 图生文(Describe)
```json
{
    "model": "midjourney/describe",
    "image": "图片base64或URL"
}
```

### 放大(Upscale)
```json
{
    "model": "midjourney/upscale",
    "index": 1,
    "task_id": "已有任务ID"
}
```

### 变体(Variation)
```json
{
    "model": "midjourney/variation", 
    "index": 1,
    "task_id": "已有任务ID"
}
```

## 注意事项

1. 所有操作都是异步的,需要通过返回的 task_id 查询结果
2. 图片操作(放大/变体等)需要原始任务的 task_id
3. 建议开启 `UPDATE_TASK` 环境变量以自动更新任务状态 