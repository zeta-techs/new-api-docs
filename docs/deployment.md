# 🚀 部署指南

## ⚡ 快速开始

### 系统要求
- CPU: 1核+
- 内存: 2GB+
- 硬盘: 1GB+
- Docker: 20.10.0+

### Docker 部署

```bash
docker run -d --name new-api \
  -p 3000:3000 \
  -v /path/to/data:/data \
  calciumion/new-api:latest
```

## 🐳 Docker Compose（推荐）

### 基础部署

```yaml
services:
  new-api:
    image: calciumion/new-api:latest
    container_name: new-api
    restart: always
    command: --log-dir /app/logs
    ports:
      - "3000:3000"
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    environment:
      - SQL_DSN=root:123456@tcp(mysql:3306)/new-api  # Point to the mysql service
      - REDIS_CONN_STRING=redis://redis
      - TZ=Asia/Shanghai
```

### 完整配置

```yaml
services:
  new-api:
    image: calciumion/new-api:latest
    container_name: new-api
    restart: always
    command: --log-dir /app/logs
    ports:
      - "3000:3000"
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    environment:
      - SQL_DSN=root:123456@tcp(mysql:3306)/new-api  # Point to the mysql service
      - REDIS_CONN_STRING=redis://redis
      - TZ=Asia/Shanghai
    #      - SESSION_SECRET=random_string  # 多机部署时设置，必须修改这个随机字符串！！！！！！！
    #      - NODE_TYPE=slave  # Uncomment for slave node in multi-node deployment
    #      - SYNC_FREQUENCY=60  # Uncomment if regular database syncing is needed
    #      - FRONTEND_BASE_URL=https://openai.justsong.cn  # Uncomment for multi-node deployment with front-end URL

    depends_on:
      - redis
      - mysql
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://localhost:3000/api/status | grep -o '\"success\":\\s*true' | awk -F: '{print $$2}'"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:latest
    container_name: redis
    restart: always

  mysql:
    image: mysql:8.2
    container_name: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: 123456  # Ensure this matches the password in SQL_DSN
      MYSQL_DATABASE: new-api
    volumes:
      - mysql_data:/var/lib/mysql
    # ports:
    #   - "3306:3306"  # If you want to access MySQL from outside Docker, uncomment

volumes:
  mysql_data:
```

## 💾 数据持久化

### 数据目录
```bash
/data/
  ├── new-api.db    # SQLite数据库文件
  ├── logs/         # 日志目录
  └── config/       # 配置文件目录
```

### 备份恢复
```bash
# 备份
tar -czf backup.tar.gz /path/to/data

# 恢复
tar -xzf backup.tar.gz -C /path/to/data
```

## 🔒 安全配置

### HTTPS 配置

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 访问控制
```nginx
# IP限制
location / {
    allow 192.168.1.0/24;
    deny all;
}

# 基础认证
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

## 📊 监控配置

### 健康检查
```bash
# 检查服务状态
curl -f http://localhost:3000/health

# 检查数据库连接
curl -f http://localhost:3000/health/db
```

### 资源监控
```yaml
# Prometheus配置
scrape_configs:
  - job_name: 'new-api'
    static_configs:
      - targets: ['localhost:3000']
```

## 🔄 更新升级

### 使用 Watchtower
```bash
# 自动更新容器
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup \
  --interval 86400
```

### 手动更新
```bash
# 拉取最新镜像
docker pull calciumion/new-api:latest

# 重启容器
docker-compose down
docker-compose up -d
```

## ⚠️ 故障排查

### 常见问题

1. 容器无法启动
   - 检查端口占用
   - 验证数据目录权限
   - 查看容器日志

2. 数据库连接失败
   - 确认数据库配置
   - 检查网络连接
   - 验证数据库权限

3. Redis连接失败
   - 检查Redis服务状态
   - 验证连接字符串
   - 确认网络可达性

### 日志查看
```bash
# 容器日志
docker logs -f new-api

# 应用日志
tail -f /path/to/data/logs/app.log
```

!!! tip "部署建议"
    1. 生产环境建议使用 Docker Compose
    2. 配置数据持久化
    3. 启用 HTTPS
    4. 设置访问控制
    5. 定期备份数据 