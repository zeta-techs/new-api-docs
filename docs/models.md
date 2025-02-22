# 模型支持

## 支持的模型类型

此版本支持以下模型:

1. OpenAI 官方模型
2. 第三方模型 **gps** (gpt-4-gizmo-*)
3. [Midjourney-Proxy(Plus)](https://github.com/novicezk/midjourney-proxy) 接口
4. [Suno API](https://github.com/Suno-API/Suno-API) 接口
5. Rerank模型 ([Cohere](https://cohere.ai/) 和 [Jina](https://jina.ai/))
6. Dify
7. Azure OpenAI
8. Anthropic Claude
9. Google Gemini

## Reasoning Effort 设置

支持通过模型名称后缀设置 reasoning effort:

- 添加后缀 `-high` 设置为 high reasoning effort (例如: `o3-mini-high`)
- 添加后缀 `-medium` 设置为 medium reasoning effort (例如: `o3-mini-medium`) 
- 添加后缀 `-low` 设置为 low reasoning effort (例如: `o3-mini-low`)

## 自定义模型

您可以在渠道中添加自定义模型,支持:

1. 填入完整调用地址
2. 自定义第三方模型(如 gpt-4-gizmo-*)

!!! note
    使用第三方模型 gpt-4-gizmo-* 时需要注意,此模型并非OpenAI官方模型,使用官方key无法调用。 

## 模型详细说明

### OpenAI 模型
支持所有 OpenAI 官方模型，包括但不限于：
- GPT-3.5 系列 (gpt-3.5-turbo等)
- GPT-4 系列 (gpt-4-turbo等)
- GPT-4V (gpt-4-vision-preview)
- DALL·E 3
- TTS (tts-1, tts-1-hd)
- Whisper (whisper-1)

### Azure OpenAI
支持部署在 Azure 上的 OpenAI 模型，需要配置：
- API版本
- 部署名称
- 资源名称
- API密钥

### Anthropic Claude
支持 Claude 系列模型：
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307
- claude-2.1
- claude-2.0
- claude-instant-1.2

### Google Gemini
支持 Gemini 系列模型：
- gemini-pro
- gemini-pro-vision
- gemini-1.5-pro-latest
- gemini-1.5-pro-001

### 自定义模型配置
可以通过在模型名称后添加后缀来配置模型行为：

1. Reasoning Effort设置：
```
模型名-{effort}

例如：
- claude-instant-1.2-high
- gemini-pro-medium
- gpt-4-low
```

2. 自定义基础URL：
在渠道编辑中可以设置完整的API调用地址，支持：
- 私有部署的模型服务
- 第三方兼容接口
- 自定义的API网关 