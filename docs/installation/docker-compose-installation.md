# 使用 Docker Compose 安装 New API

本文档将指导您如何使用 Docker Compose 快速安装和部署 New API 服务。Docker Compose 是推荐的部署方式，因为它简化了配置并便于管理依赖服务。

## 前提条件

- 已安装 Docker 和 Docker Compose
- 服务器或本地环境可以连接互联网
- 基本了解 Docker 和 Linux 命令行操作

## 安装步骤

### 1. 安装 Docker 和 Docker Compose

如果尚未安装 Docker 和 Docker Compose，请参考以下命令或官方文档安装：

#### Linux

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Windows/macOS

直接从 [Docker 官网](https://www.docker.com/products/docker-desktop) 下载并安装 Docker Desktop，它已包含 Docker Compose。

### 2. 获取 New API 项目

#### 方法一：克隆 GitHub 仓库

```bash
git clone https://github.com/Calcium-Ion/new-api.git
cd new-api
```

#### 方法二：手动创建 Docker Compose 文件

如果不想克隆整个仓库，可以创建一个新目录，然后在其中创建 `docker-compose.yml` 文件：

```bash
mkdir new-api
cd new-api
```

创建 `docker-compose.yml` 文件，内容如下：

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

### 3. 自定义配置（可选）

在启动前，您可以根据需要修改 `docker-compose.yml` 文件，常见的自定义配置包括：

- 更改端口映射
- 使用外部数据库
- 设置 Redis 缓存
- 配置环境变量

#### 使用 SQLite 数据库（默认）

无需额外配置，New API 默认使用 SQLite 数据库，数据存储在 `/data` 目录下。

#### 使用 MySQL 数据库

编辑 `docker-compose.yml` 文件，添加 MySQL 服务并配置连接：

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
      - SQL_DSN=root:mysql_password@tcp(mysql:3306)/oneapi
    volumes:
      - ./data:/data
    depends_on:
      - mysql

  mysql:
    image: mysql:8
    container_name: new-api-mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=mysql_password
      - MYSQL_DATABASE=oneapi
    volumes:
      - ./mysql-data:/var/lib/mysql
```

#### 添加 Redis 缓存（推荐用于生产环境）

编辑 `docker-compose.yml` 文件，添加 Redis 服务并配置连接：

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
      - REDIS_CONN_STRING=redis://redis:6379/1
      - MEMORY_CACHE_ENABLED=true
    volumes:
      - ./data:/data
    depends_on:
      - redis

  redis:
    image: redis:alpine
    container_name: new-api-redis
    restart: always
    volumes:
      - ./redis-data:/data
```

### 4. 启动服务

在 `docker-compose.yml` 文件所在目录中执行以下命令启动服务：

```bash
docker-compose up -d
```

该命令会以守护进程模式启动所有服务，`-d` 参数表示在后台运行。

### 5. 验证服务状态

启动后，可以通过以下命令检查服务状态：

```bash
docker-compose ps
```

输出应显示 new-api 容器处于 "Up" 状态。

您也可以查看服务日志：

```bash
docker-compose logs new-api
# 或者实时查看日志
docker-compose logs -f new-api
```

### 6. 访问 New API

服务启动后，可以通过浏览器访问：

```
http://your-server-ip:3000
```

默认管理员账号：`root`  
默认管理员密码：`123456`

## 管理服务

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 更新 New API 到最新版本

```bash
# 拉取最新镜像
docker-compose pull

# 重新创建容器
docker-compose up -d
```

### 查看数据存储位置

默认情况下，New API 的数据存储在当前目录的 `data` 文件夹中。SQLite 数据库文件路径为 `./data/one-api.db`。

## 高级配置

### 配置 HTTPS

推荐通过反向代理（如 Nginx 或 Traefik）配置 HTTPS，但您也可以在 New API 上直接配置。

编辑 `docker-compose.yml`，添加证书挂载和相关环境变量：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    environment:
      - TZ=Asia/Shanghai
      - CERT_FILE=/data/certs/cert.pem
      - KEY_FILE=/data/certs/key.pem
    volumes:
      - ./data:/data
      - ./certs:/data/certs
```

### 调整日志级别

可以通过环境变量调整日志级别：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    environment:
      - TZ=Asia/Shanghai
      - LOG_LEVEL=info  # 可选值: debug, info, warn, error
```

### 多机部署配置

多机部署时，需要确保所有实例共享相同的密钥和数据库：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    environment:
      - TZ=Asia/Shanghai
      - SESSION_SECRET=same-secret-key-for-all-instances
      - CRYPTO_SECRET=same-crypto-key-for-all-instances
      - SQL_DSN=root:password@tcp(shared-mysql-host:3306)/oneapi
      - REDIS_CONN_STRING=redis://shared-redis-host:6379/1
```

## 常见问题

### 数据库迁移问题

如果从 SQLite 迁移到 MySQL，可以使用以下步骤：

1. 备份当前 SQLite 数据库
2. 配置 MySQL 连接
3. 使用迁移工具或手动导入数据

### 容器无法启动

检查日志以了解问题：

```bash
docker-compose logs new-api
```

常见原因包括：
- 端口冲突（已被其他服务占用）
- 数据库连接失败
- 目录权限问题

### 内存不足

如果服务器内存有限，可以限制容器使用的内存：

```yaml
services:
  new-api:
    # ... 其他配置 ...
    deploy:
      resources:
        limits:
          memory: 512M
```

## 更多资源

- [Docker Compose 配置详解](./docker-compose-configuration.md)
- [系统设置指南](../user-guide/system-settings.md)
- [渠道配置教程](../user-guide/channel-configuration.md)
