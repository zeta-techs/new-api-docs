# 宝塔面板部署指南

## 🚀 快速开始

### 系统要求

!!! note "环境准备"
    - 已安装宝塔面板
    - 已安装 Docker 管理器
    - 已安装 Nginx
    - 已安装 MySQL/SQLite

### 安装步骤

1. 创建网站
   ```bash
   # 在宝塔面板中创建网站
   域名: your-domain.com
   端口: 80,443
   PHP版本: 纯静态
   ```

2. 安装 Docker
   ```bash
   # 在软件商店搜索并安装 Docker 管理器
   宝塔面板 -> 软件商店 -> Docker管理器 -> 安装
   ```

## 📦 部署容器

### 使用 Docker 管理器

1. 创建容器
   ```yaml
   名称: new-api
   镜像: calciumion/new-api:latest
   端口: 3000:3000
   目录映射: 
     - /www/docker/new-api/data:/data
   环境变量:
     - TZ=Asia/Shanghai
     - SQL_DSN=sqlite:///data/new-api.db
   ```

2. 启动容器
   ```bash
   # 在 Docker 管理器中启动容器
   容器列表 -> new-api -> 启动
   ```

### Nginx 配置

1. 编辑网站配置
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:3000;
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

2. 配置 SSL
   ```bash
   # 在网站设置中申请SSL证书
   网站 -> SSL -> Let's Encrypt -> 申请
   ```

## ⚙️ 环境配置

### 数据库配置

=== "SQLite (默认)"
    ```bash
    # 环境变量配置
    SQL_DSN=sqlite:///data/new-api.db
    ```

=== "MySQL"
    ```bash
    # 创建数据库
    数据库名：new_api
    字符集：utf8mb4
    排序规则：utf8mb4_general_ci
    
    # 环境变量配置
    SQL_DSN=root:password@tcp(localhost:3306)/new_api
    ```

### Redis 配置 (可选)

```bash
# 安装 Redis
宝塔面板 -> 软件商店 -> Redis -> 安装

# 环境变量配置
REDIS_CONN_STRING=redis://:password@localhost:6379
```

## 🔒 安全配置

### 防火墙设置

1. 开放端口
   ```bash
   # 在安全页面开放端口
   安全 -> 防火墙 -> 添加规则
   端口: 3000
   描述: New API服务
   ```

2. 设置访问控制
   ```nginx
   # 在网站配置中添加IP限制
   location / {
       allow 192.168.1.0/24;  # 允许内网访问
       deny all;              # 禁止其他访问
   }
   ```

### SSL 配置

```nginx
# 强制 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
}
```

## 📊 监控管理

### 日志查看

```bash
# 容器日志
Docker管理器 -> 容器列表 -> new-api -> 日志

# Nginx访问日志
网站 -> 日志 -> access.log
```

### 性能监控

1. 系统监控
   ```bash
   # 在监控页面查看
   监控 -> 系统监控
   ```

2. 网站监控
   ```bash
   # 在网站设置中开启监控
   网站 -> 设置 -> 性能监控
   ```

## 💾 数据备份

### 自动备份

1. 创建备份任务
   ```bash
   # 在计划任务中添加
   计划任务 -> 添加计划任务
   
   # 备份命令
   tar -czf /www/backup/new-api-$(date +\%Y\%m\%d).tar.gz /www/docker/new-api/data
   ```

2. 设置定时
   ```bash
   # 每天凌晨2点备份
   0 2 * * * /path/to/backup.sh
   ```

### 数据恢复

```bash
# 停止容器
Docker管理器 -> 容器列表 -> new-api -> 停止

# 恢复数据
tar -xzf /www/backup/new-api-20240101.tar.gz -C /www/docker/new-api/

# 启动容器
Docker管理器 -> 容器列表 -> new-api -> 启动
```

!!! tip "部署建议"
    1. 定期更新系统和面板
    2. 配置自动备份
    3. 开启系统监控
    4. 及时安装安全补丁
    5. 使用强密码和SSL 