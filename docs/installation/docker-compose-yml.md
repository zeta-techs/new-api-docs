# 📄 Docker Compose 配置说明

本文档详细介绍了New API的Docker Compose配置选项，可用于多种部署场景。

## 🧱 基本配置结构

Docker Compose配置文件 `docker-compose.yml` 定义了New API服务及其依赖服务（如MySQL、Redis）的部署方式。

## 🏭 标准配置（推荐生产环境）

下面是标准的Docker Compose配置，适合大多数生产环境：

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
      - SQL_DSN=root:123456@tcp(mysql:3306)/new-api  # 指向mysql服务
      - REDIS_CONN_STRING=redis://redis
      - TZ=Asia/Shanghai
    #      - SESSION_SECRET=random_string  # 多机部署时设置，必须修改这个随机字符串！！！！！！！
    #      - NODE_TYPE=slave  # 多机部署的从节点取消注释
    #      - SYNC_FREQUENCY=60  # 如需定期同步数据库，取消注释
    #      - FRONTEND_BASE_URL=https://your-domain.com  # 多机部署带前端URL时取消注释

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
      MYSQL_ROOT_PASSWORD: 123456  # 确保与SQL_DSN中的密码一致
      MYSQL_DATABASE: new-api
    volumes:
      - mysql_data:/var/lib/mysql
    # ports:
    #   - "3306:3306"  # 如需从Docker外部访问MySQL，取消注释

volumes:
  mysql_data:
```

## 🧪 简化配置（适合测试环境）

如果只是测试使用，可以采用以下简化版本，仅包含New API服务本身：

```yaml
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

## ⚙️ 配置说明

### 🔧 New API服务配置

| 参数 | 说明 |
|------|------|
| `image` | 镜像名称，通常使用`calciumion/new-api:latest`获取最新版本 |
| `container_name` | 容器名称，可自定义 |
| `restart` | 容器重启策略，建议设为`always`确保服务自动重启 |
| `command` | 启动命令，可自定义启动参数 |
| `ports` | 端口映射，默认将容器内3000端口映射到主机3000端口 |
| `volumes` | 数据卷映射，确保数据持久化 |
| `environment` | 环境变量设置，用于配置New API行为 |
| `depends_on` | 依赖服务，确保按正确顺序启动 |
| `healthcheck` | 健康检查配置，用于监控服务状态 |

### 🔍 环境变量说明

New API支持多种环境变量配置，以下是常用的几个：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `SQL_DSN` | 数据库连接字符串 | `root:123456@tcp(mysql:3306)/new-api` |
| `REDIS_CONN_STRING` | Redis连接字符串 | `redis://redis` |
| `TZ` | 时区设置 | `Asia/Shanghai` |
| `SESSION_SECRET` | 会话密钥(多机部署必须) | `your_random_string` |
| `NODE_TYPE` | 节点类型(主/从) | `master`或`slave` |
| `SYNC_FREQUENCY` | 同步频率(秒) | `60` |

更完整的环境变量列表请参考[环境变量配置指南](environment-variables.md)。

## 🌐 多节点部署配置

对于多节点部署场景，主节点和从节点的配置略有不同：

### 👑 主节点配置

```yaml
services:
  new-api-master:
    image: calciumion/new-api:latest
    container_name: new-api-master
    restart: always
    ports:
      - "3000:3000"
    environment:
      - SQL_DSN=root:123456@tcp(mysql:3306)/new-api
      - REDIS_CONN_STRING=redis://redis
      - SESSION_SECRET=your_unique_session_secret
      - CRYPTO_SECRET=your_unique_crypto_secret
      - TZ=Asia/Shanghai
    volumes:
      - ./data:/data
```

### 👥 从节点配置

```yaml
services:
  new-api-slave:
    image: calciumion/new-api:latest
    container_name: new-api-slave
    restart: always
    ports:
      - "3001:3000"  # 注意端口映射不同
    environment:
      - SQL_DSN=root:123456@tcp(mysql:3306)/new-api
      - REDIS_CONN_STRING=redis://redis
      - SESSION_SECRET=your_unique_session_secret  # 必须与主节点相同
      - CRYPTO_SECRET=your_unique_crypto_secret  # 必须与主节点相同
      - NODE_TYPE=slave  # 设置为从节点
      - SYNC_FREQUENCY=60
      - TZ=Asia/Shanghai
    volumes:
      - ./data-slave:/data
```

## 📝 使用方法

### ⬇️ 安装

将配置保存为`docker-compose.yml`文件，然后在同一目录下运行：

```bash
docker compose up -d
```

### 📋 查看日志

```bash
docker compose logs -f
```

### 🛑 停止服务

```bash
docker compose down
```

!!! tip "提示"
    更多关于Docker Compose的使用方法，请参考[Docker Compose安装指南](docker-compose-installation.md)。
