# ⚙️ 配置说明

## 🔧 环境变量配置

### 核心配置
| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `GENERATE_DEFAULT_TOKEN` | 新用户生成初始令牌 | `false` | `true` |
| `STREAMING_TIMEOUT` | 流式响应超时时间(秒) | `60` | `120` |
| `FORCE_STREAM_OPTION` | 强制覆盖客户端stream参数 | `true` | `false` |
| `GET_MEDIA_TOKEN` | 统计图片token | `true` | `false` |
| `GET_MEDIA_TOKEN_NOT_STREAM` | 非流情况下统计图片token | `true` | `false` |
| `UPDATE_TASK` | 更新异步任务状态 | `true` | `false` |

### 🤖 模型配置
| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `GEMINI_MODEL_MAP` | Gemini模型版本指定 | `v1beta` | `gemini-1.5-pro-latest:v1beta` |
| `COHERE_SAFETY_SETTING` | Cohere安全等级 | `NONE` | `STRICT` |
| `GEMINI_VISION_MAX_IMAGE_NUM` | Gemini最大图片数量 | `16` | `-1` |
| `MAX_FILE_DOWNLOAD_MB` | 最大文件下载大小(MB) | `20` | `50` |
| `AZURE_DEFAULT_API_VERSION` | Azure默认API版本 | `2024-12-01-preview` | `2023-12-01` |

### 🔔 通知配置
| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `NOTIFICATION_LIMIT_DURATION_MINUTE` | 通知限制时间(分钟) | `10` | `30` |
| `NOTIFY_LIMIT_COUNT` | 时间内最大通知数 | `2` | `5` |

### 🛠️ 调试配置
| 环境变量 | 说明 | 默认值 | 示例 |
|---------|------|--------|------|
| `DIFY_DEBUG` | Dify工作流调试 | `true` | `false` |

### 🔒 安全配置
| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `CRYPTO_SECRET` | 加密密钥 | `your-secret-key` |
| `SESSION_SECRET` | 会话密钥 | `your-session-key` |

## 💾 缓存配置

### Redis缓存（推荐）
```bash
# Redis连接配置
REDIS_CONN_STRING=redis://default:password@localhost:6379

# Redis缓存配置
REDIS_CACHE_TTL=3600  # 缓存过期时间(秒)
REDIS_MAX_RETRIES=3   # 最大重试次数
```

### 内存缓存
```bash
# 启用内存缓存
MEMORY_CACHE_ENABLED=true

# 内存缓存配置
MEMORY_CACHE_SIZE=1000  # 最大缓存条目数
MEMORY_CACHE_TTL=3600   # 缓存过期时间(秒)
```

## 🌐 多机部署

### 基础要求
!!! warning "重要提示"
    - 必须设置 `SESSION_SECRET` 确保登录状态一致
    - 共用Redis时必须设置 `CRYPTO_SECRET`
    - 所有实例环境变量配置必须一致

### 数据库配置
```bash
# MySQL示例
SQL_DSN="user:pass@tcp(host:3306)/dbname"

# PostgreSQL示例
SQL_DSN="postgres://user:pass@host:5432/dbname"
```

### 会话和加密配置
```bash
# 设置会话密钥（必需）
SESSION_SECRET=your_session_secret

# 设置加密密钥（使用Redis时必需）
CRYPTO_SECRET=your_crypto_secret
```

### 负载均衡
```nginx
upstream new_api {
    server 192.168.1.1:3000;
    server 192.168.1.2:3000;
    ip_hash;  # 会话保持
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
!!! tip "多机部署建议"
    1. 使用共享的MySQL/PostgreSQL数据库
    2. 使用共享的Redis缓存
    3. 确保所有实例的环境变量配置一致
    4. 配置合适的负载均衡策略

## 📝 日志配置

### 日志级别
```bash
# 可选值: debug, info, warn, error
LOG_LEVEL=info
LOG_PATH=/path/to/logs
```

### 日志轮转
```bash
# logrotate配置
/path/to/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

## 🚨 告警配置

### 基础告警
```yaml
alerts:
  error_rate:
    threshold: 5%
    window: 5m
  response_time:
    threshold: 1s
    window: 1m
```

### 通知限制
```bash
# 通知频率限制
NOTIFICATION_LIMIT_DURATION_MINUTE=10  # 限制时间窗口
NOTIFY_LIMIT_COUNT=2                   # 最大通知数量
```

## 🚀 性能优化

### 连接池配置
```bash
# 数据库连接池
DB_MAX_CONNECTIONS=100
DB_MAX_IDLE_CONNECTIONS=10

# Redis连接池
REDIS_MAX_CONNECTIONS=100
```

### 超时配置
```bash
# API超时时间(秒)
API_TIMEOUT=30

# 流式响应超时
STREAMING_TIMEOUT=60
```

## 🛡️ 安全配置

### 密码策略
```bash
# 最小密码长度
MIN_PASSWORD_LENGTH=8

# 密码复杂度要求
PASSWORD_STRENGTH=medium  # simple, medium, strong
```

### 访问控制
```bash
# IP白名单
ALLOWED_IPS=127.0.0.1,192.168.1.*

# 请求频率限制
RATE_LIMIT=100/minute
```

!!! tip "配置建议"
    1. 生产环境必须修改默认密码
    2. 建议启用HTTPS
    3. 配置适当的访问控制策略
    4. 定期备份数据
    5. 监控系统资源使用
    6. 设置合理的限流策略

## 🔌 环境变量配置

### 基础配置
- `GENERATE_DEFAULT_TOKEN`：是否为新注册用户生成初始令牌，默认为 `false`
- `STREAMING_TIMEOUT`：设置流式一次回复的超时时间，默认为 60 秒
- `DIFY_DEBUG`：设置 Dify 渠道是否输出工作流和节点信息到客户端，默认为 `true`
- `GET_MEDIA_TOKEN_NOT_STREAM`：是否在非流情况下统计图片token，默认为 `true`
- `UPDATE_TASK`：是否更新异步任务，默认为 `true`

### 模型相关配置
- `GEMINI_MODEL_MAP`：Gemini模型指定版本(v1/v1beta)
- `COHERE_SAFETY_SETTING`：Cohere模型安全设置
- `GEMINI_VISION_MAX_IMAGE_NUM`：Gemini模型最大图片数量，默认为 `16`
- `MAX_FILE_DOWNLOAD_MB`: 最大文件下载大小，默认为 `20` MB

### API版本配置
- `AZURE_DEFAULT_API_VERSION`：Azure渠道默认API版本，默认为 `2024-12-01-preview`

### 通知配置
- `NOTIFICATION_LIMIT_DURATION_MINUTE`：通知限制的持续时间（分钟），默认为 `10`
- `NOTIFY_LIMIT_COUNT`：用户通知在指定持续时间内的最大数量，默认为 `2`

## 🌍 多机部署配置

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