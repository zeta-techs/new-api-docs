# 配置说明

## 环境变量配置

### 基础配置
- `GENERATE_DEFAULT_TOKEN`：是否为新注册用户生成初始令牌，默认为 `false`
- `STREAMING_TIMEOUT`：设置流式一次回复的超时时间，默认为 60 秒
- `DIFY_DEBUG`：设置 Dify 渠道是否输出工作流和节点信息到客户端，默认为 `true`
- `FORCE_STREAM_OPTION`：是否覆盖客户端stream_options参数，默认为 `true`
- `GET_MEDIA_TOKEN`：是否统计图片token，默认为 `true`
- `GET_MEDIA_TOKEN_NOT_STREAM`：是否在非流情况下统计图片token，默认为 `true`
- `UPDATE_TASK`：是否更新异步任务，默认为 `true`

### 模型相关配置
- `GEMINI_MODEL_MAP`：Gemini模型指定版本(v1/v1beta)
- `COHERE_SAFETY_SETTING`：Cohere模型安全设置
- `GEMINI_VISION_MAX_IMAGE_NUM`：Gemini模型最大图片数量，默认为 `16`
- `MAX_FILE_DOWNLOAD_MB`: 最大文件下载大小，默认为 `20` MB

### 安全相关配置
- `CRYPTO_SECRET`：加密密钥，用于加密数据库内容
- `SESSION_SECRET`：会话密钥，多机部署必须设置

### API版本配置
- `AZURE_DEFAULT_API_VERSION`：Azure渠道默认API版本，默认为 `2024-12-01-preview`

### 通知配置
- `NOTIFICATION_LIMIT_DURATION_MINUTE`：通知限制的持续时间（分钟），默认为 `10`
- `NOTIFY_LIMIT_COUNT`：用户通知在指定持续时间内的最大数量，默认为 `2`

## 缓存配置

### Redis缓存
设置 `REDIS_CONN_STRING` 启用Redis缓存：
``
REDIS_CONN_STRING=redis://default:redispw@localhost:49153
``

### 内存缓存
设置 `MEMORY_CACHE_ENABLED=true` 启用内存缓存（如果已设置Redis则无需设置） 

## 多机部署配置

### 会话配置
必须设置 `SESSION_SECRET` 环境变量，确保多机之间的登录状态一致：
```shell
SESSION_SECRET=your_session_secret
```

### Redis共享配置
当多机共用Redis时，必须设置 `CRYPTO_SECRET`：
```shell
CRYPTO_SECRET=your_crypto_secret
```

### 负载均衡
建议使用 Nginx 等反向代理进行负载均衡，示例配置：
```nginx
upstream new_api {
    server 192.168.1.1:3000;
    server 192.168.1.2:3000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://new_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 数据同步
多机部署时建议：
1. 使用共享的MySQL/PostgreSQL数据库
2. 使用共享的Redis缓存
3. 确保所有实例的环境变量配置一致 