# Docker Compose 配置详解

本文档详细介绍 New API 的 Docker Compose 配置选项和高级设置。

## 基本配置文件

以下是一个基本的 `docker-compose.yml` 文件示例：

```yaml
version: '3'

services:
  new-api:
    image: calciumion/new-api:latest
    container_name: new-api
    restart: always
    ports:
      - "3000:3000"
    environment:
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/data
```

## 完整配置选项

以下是包含所有常用配置选项的更完整 `docker-compose.yml` 文件：

```yaml
version: '3'

services:
  new-api:
    image: calciumion/new-api:latest
    container_name: new-api
    restart: always
    ports:
      - "3000:3000"
    environment:
      # 基本设置
      - TZ=Asia/Shanghai
      - PORT=3000
      - SQL_DSN=sqlite3:///data/one-api.db
      # 安全设置
      - SESSION_SECRET=your-session-secret-key
      - FRONTEND_BASE_URL=https://your-domain.com
      # 缓存设置
      - REDIS_CONN_STRING=redis://redis:6379/1
      - MEMORY_CACHE_ENABLED=true
      # 特定功能设置
      - GENERATE_DEFAULT_TOKEN=false
      - STREAMING_TIMEOUT=60
      - DIFY_DEBUG=true
      - FORCE_STREAM_OPTION=true
      - GET_MEDIA_TOKEN=true
      - GET_MEDIA_TOKEN_NOT_STREAM=true
      - UPDATE_TASK=true
      - COHERE_SAFETY_SETTING=NONE
      - GEMINI_VISION_MAX_IMAGE_NUM=16
      - MAX_FILE_DOWNLOAD_MB=20
      - CRYPTO_SECRET=your-crypto-secret-key
      - AZURE_DEFAULT_API_VERSION=2024-12-01-preview
      - NOTIFICATION_LIMIT_DURATION_MINUTE=10
      - NOTIFY_LIMIT_COUNT=2
    volumes:
      - ./data:/data
    depends_on:
      - redis
      - mysql
    networks:
      - new-api-network

  redis:
    image: redis:alpine
    container_name: new-api-redis
    restart: always
    volumes:
      - ./redis-data:/data
    networks:
      - new-api-network

  mysql:
    image: mysql:8
    container_name: new-api-mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=your-mysql-password
      - MYSQL_DATABASE=oneapi
    volumes:
      - ./mysql-data:/var/lib/mysql
    networks:
      - new-api-network

networks:
  new-api-network:
    driver: bridge
```

## 配置项说明

### 基本配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `PORT` | 服务监听端口 | `3000` |
| `TZ` | 时区设置 | `Asia/Shanghai` |
| `SQL_DSN` | 数据库连接字符串 | `sqlite3:///data/one-api.db` |

### 数据库配置

#### SQLite 配置（默认）
```yaml
environment:
  - SQL_DSN=sqlite3:///data/one-api.db
```

#### MySQL 配置
```yaml
environment:
  - SQL_DSN=root:password@tcp(mysql:3306)/oneapi
```

#### PostgreSQL 配置
```yaml
environment:
  - SQL_DSN=postgres://username:password@postgres:5432/oneapi
```

### 缓存配置

缓存配置可以显著提高性能和稳定性，特别是在使用渠道重试功能时：

```yaml
environment:
  - REDIS_CONN_STRING=redis://redis:6379/1
  - MEMORY_CACHE_ENABLED=true
```

### 安全配置

多机部署必备的安全配置：

```yaml
environment:
  - SESSION_SECRET=your-session-secret-key
  - CRYPTO_SECRET=your-crypto-secret-key
```

### 特定功能配置

```yaml
environment:
  # 为新用户自动生成令牌
  - GENERATE_DEFAULT_TOKEN=true
  # 流式响应超时时间（秒）
  - STREAMING_TIMEOUT=60
  # Dify 调试模式
  - DIFY_DEBUG=true
  # 强制使用流式选项
  - FORCE_STREAM_OPTION=true
  # 是否统计媒体文件 token
  - GET_MEDIA_TOKEN=true
  # 非流模式下是否统计媒体文件 token
  - GET_MEDIA_TOKEN_NOT_STREAM=true
  # 是否更新异步任务（MJ、Suno）
  - UPDATE_TASK=true
  # Cohere 安全设置
  - COHERE_SAFETY_SETTING=NONE
  # Gemini 最大图片数
  - GEMINI_VISION_MAX_IMAGE_NUM=16
  # 最大文件下载大小（MB）
  - MAX_FILE_DOWNLOAD_MB=20
  # Azure 默认 API 版本
  - AZURE_DEFAULT_API_VERSION=2024-12-01-preview
  # 通知限制持续时间（分钟）
  - NOTIFICATION_LIMIT_DURATION_MINUTE=10
  # 通知限制数量
  - NOTIFY_LIMIT_COUNT=2
```

## 使用外部服务

New API 可以与多种外部服务集成。以下是一些常见的配置示例：

### 使用外部 Redis

```yaml
environment:
  - REDIS_CONN_STRING=redis://username:password@redis-host:6379/1
```

### 使用外部 MySQL

```yaml
environment:
  - SQL_DSN=root:password@tcp(mysql-host:3306)/oneapi
```

### 使用外部 PostgreSQL

```yaml
environment:
  - SQL_DSN=postgres://username:password@postgres-host:5432/oneapi
```

## 健康检查配置

可以添加健康检查以提高服务的可靠性：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 多实例部署

对于高负载场景，可以考虑使用多实例部署：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    deploy:
      mode: replicated
      replicas: 3
```

## 持久化存储

推荐使用命名卷进行数据持久化：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    volumes:
      - new-api-data:/data

volumes:
  new-api-data:
    driver: local
```

## 使用技巧

### 环境变量文件

可以使用 `.env` 文件管理环境变量：

```yaml
services:
  new-api:
    env_file:
      - .env
```

`.env` 文件示例：
```
TZ=Asia/Shanghai
SQL_DSN=root:password@tcp(mysql:3306)/oneapi
SESSION_SECRET=your-secret-key
REDIS_CONN_STRING=redis://redis:6379/1
```

### 资源限制

限制容器使用的资源：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 故障排除

如果遇到配置问题，可尝试以下步骤：

1. 查看容器日志：
   ```bash
   docker-compose logs new-api
   ```

2. 检查网络连接：
   ```bash
   docker-compose exec new-api ping redis
   docker-compose exec new-api ping mysql
   ```

3. 验证数据库连接：
   ```bash
   docker-compose exec mysql mysql -u root -p -e "SHOW DATABASES;"
   ```

## 下一步

- [渠道配置](../user-guide/channel-configuration.md)
- [令牌管理](../user-guide/token-management.md)
- [系统设置](../user-guide/system-settings.md)
