# Suno API 接入指南

## 简介

[Suno API](https://github.com/Suno-AI/Suno-API) 是一个AI音乐生成服务。通过 New API,你可以方便地接入 Suno 的服务。

## 配置步骤

### 1. 获取 Suno API 密钥
前往 [Suno](https://suno.ai) 注册账号并获取 API 密钥。

### 2. 添加渠道
在 New API 管理后台:

1. 进入`渠道管理`
2. 点击`新建渠道`
3. 选择类型为`Suno`
4. 填写配置信息:
   - 名称: 自定义渠道名称
   - 密钥: Suno API 密钥
   - 其他选项可按需配置

### 3. 支持的模型
添加渠道后,系统会自动创建以下模型:

- `suno/bark`: Bark 模型
- `suno/musicgen`: MusicGen 模型

## 调用示例

### 使用 Bark 生成音频
```json
{
    "model": "suno/bark",
    "prompt": "你的音频生成提示词"
}
```

### 使用 MusicGen 生成音乐
```json
{
    "model": "suno/musicgen",
    "prompt": "你的音乐生成提示词"
}
```

## 注意事项

1. 音频生成是异步操作,需要通过返回的 task_id 查询结果
2. 建议开启 `UPDATE_TASK` 环境变量以自动更新任务状态
3. 生成的音频文件会以 base64 格式返回 