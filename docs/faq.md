# 常见问题解答

## 🚀 快速导航

=== "部署相关"
    - [如何选择数据库？](#database-choice)
    - [为什么会出现连接超时？](#timeout-issues)
    - [如何配置HTTPS？](#https-setup)
    - [如何进行数据备份？](#data-backup)

=== "渠道相关"
    - [如何添加新渠道？](#add-channel)
    - [如何处理渠道轮询？](#channel-polling)
    - [渠道余额不足怎么办？](#channel-balance)
    - [如何设置渠道优先级？](#channel-priority)

=== "功能相关"
    - [如何限制用户额度？](#quota-limit)
    - [如何确保数据安全？](#data-security)
    - [如何监控系统状态？](#system-monitoring)
    - [如何处理并发请求？](#concurrent-requests)

## 💾 部署问题

### 数据库选择 {#database-choice}

!!! question "如何选择合适的数据库？"

=== "SQLite"
    ✅ 推荐场景：
    - 单机部署
    - 轻量级使用
    - 快速测试

    ❌ 不适用场景：
    - 高并发访问
    - 多机部署
    - 大规模数据

=== "MySQL"
    ✅ 推荐场景：
    - 多机部署
    - 中等规模使用
    - 需要主从复制

    配置示例：
    ```bash
    SQL_DSN="user:pass@tcp(host:3306)/dbname"
    ```

=== "PostgreSQL"
    ✅ 推荐场景：
    - 高并发场景
    - 需要复杂查询
    - 大规模部署

    配置示例：
    ```bash
    SQL_DSN="postgres://user:pass@host:5432/dbname"
    ```

### 连接超时问题 {#timeout-issues}

!!! question "为什么会出现连接超时？"

可能的原因：
1. 网络问题
2. 上游服务响应慢
3. 配置的超时时间过短

解决方案：

```nginx
# Nginx配置
location / {
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

```bash
# 环境变量配置
STREAMING_TIMEOUT=60
API_TIMEOUT=30
```

## 🔄 渠道管理

### 添加新渠道 {#add-channel}

!!! question "如何添加和配置新渠道？"

1. 进入管理后台
2. 选择"渠道管理"
3. 点击"新建渠道"
4. 填写配置信息：
   ```json
   {
     "name": "渠道名称",
     "type": "渠道类型",
     "key": "API密钥",
     "base_url": "基础URL",
     "weight": 100
   }
   ```

### 渠道轮询策略 {#channel-polling}

!!! question "如何配置渠道轮询？"

系统提供两种策略：

1. 优先级策略
   ```json
   {
     "strategy": "priority",
     "channels": [
       {"name": "channel1", "priority": 1},
       {"name": "channel2", "priority": 2}
     ]
   }
   ```

2. 权重策略
   ```json
   {
     "strategy": "weight",
     "channels": [
       {"name": "channel1", "weight": 70},
       {"name": "channel2", "weight": 30}
     ]
   }
   ```

## 🛡️ 安全配置

### 用户额度限制 {#quota-limit}

!!! question "如何实现用户额度限制？"

可以通过以下方式：

1. 用户组配额
   ```json
   {
     "group": "basic",
     "quota": 100000,
     "rate_limit": "100/minute"
   }
   ```

2. 令牌限制
   ```json
   {
     "token": "api-key",
     "quota": 50000,
     "expires_in": "30d"
   }
   ```

### 数据安全保护 {#data-security}

!!! tip "数据安全建议"

1. 加密配置
   ```bash
   # 设置加密密钥
   CRYPTO_SECRET=your-secret-key
   
   # 启用HTTPS
   USE_HTTPS=true
   ```

2. 访问控制
   ```bash
   # IP白名单
   ALLOWED_IPS=127.0.0.1,192.168.1.*
   
   # 请求限制
   RATE_LIMIT=100/minute
   ```

## 📊 监控告警

### 系统监控 {#system-monitoring}

!!! question "如何监控系统状态？"

1. 性能指标
   - CPU使用率
   - 内存占用
   - 请求延迟
   - 错误率

2. 告警配置
   ```yaml
   alerts:
     error_rate:
       threshold: 5%
       window: 5m
     response_time:
       threshold: 1s
       window: 1m
   ```

### 日志管理

```bash
# 日志配置
LOG_LEVEL=info
LOG_PATH=/path/to/logs

# 日志轮转
logrotate -d /etc/logrotate.d/new-api
```

## 💡 使用技巧

### 性能优化

1. 缓存配置
   ```bash
   # Redis缓存
   REDIS_CONN_STRING=redis://localhost:6379
   REDIS_CACHE_TTL=3600
   ```

2. 连接池设置
   ```bash
   # 数据库连接池
   DB_MAX_CONNECTIONS=100
   DB_MAX_IDLE_CONNECTIONS=10
   ```

### 故障恢复

1. 数据备份
   ```bash
   # 自动备份脚本
   0 2 * * * tar -czf backup-$(date +%Y%m%d).tar.gz /data
   ```

2. 服务恢复
   ```bash
   # 重启服务
   docker-compose down
   docker-compose up -d
   ```

!!! tip "最佳实践"
    1. 定期检查系统日志
    2. 及时更新系统版本
    3. 做好数据备份
    4. 配置监控告警
    5. 制定应急预案 