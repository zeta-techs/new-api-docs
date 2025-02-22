# Rerank 接入指南

## 简介

Rerank 是一种重新排序技术,可以优化搜索结果的相关性。New API 目前支持:
- [Cohere](https://cohere.ai/) Rerank
- [Jina](https://jina.ai/) Rerank

## Cohere Rerank 配置

### 1. 获取 API 密钥
前往 [Cohere](https://cohere.ai/) 注册账号并获取 API 密钥。

### 2. 添加渠道
1. 进入`渠道管理`
2. 点击`新建渠道`
3. 选择类型为`Cohere`
4. 填写配置:
   - 名称: 自定义渠道名称
   - 密钥: Cohere API 密钥
   - 其他选项可按需配置

## Jina Rerank 配置

### 1. 获取 API 密钥
前往 [Jina](https://jina.ai/) 注册账号并获取 API 密钥。

### 2. 添加渠道
配置步骤同 Cohere,但选择类型为`Jina`。

## 调用示例

### Cohere Rerank
```json
{
    "model": "rerank-english-v2.0",
    "query": "搜索查询",
    "documents": [
        "文档1",
        "文档2",
        "文档3"
    ]
}
```

### Jina Rerank
```json
{
    "model": "jina-rerank-v1-base-en",
    "query": "搜索查询",
    "documents": [
        "文档1",
        "文档2",
        "文档3"
    ]
}
```

## 注意事项

1. Cohere 支持设置安全等级,通过环境变量 `COHERE_SAFETY_SETTING` 配置
2. 返回结果包含相关性得分,可用于结果排序
3. 建议对大量文档进行批处理以提高效率 