# 使用 Docker 安装 New API

本文档详细介绍如何使用 Docker 安装和配置 New API。

## 系统要求

- 已安装 Docker（版本 20.10 或更高）
- 能够访问互联网，或者有本地 Docker 镜像

## 安装 Docker

如果您尚未安装 Docker，请按照以下步骤安装：

### Linux（以 Ubuntu 为例）

```bash
# 更新软件包索引
sudo apt-get update

# 安装必要的依赖
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 的官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 设置 Docker 仓库
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 再次更新软件包索引
sudo apt-get update

# 安装最新版本的 Docker Engine
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 验证 Docker 是否安装成功
sudo docker run hello-world
```

### Windows 和 macOS

从 [Docker 官网](https://www.docker.com/products/docker-desktop/) 下载并安装 Docker Desktop。

## 使用 Docker 安装 New API

### 方法一：使用官方镜像（推荐）

```bash
# 拉取最新的 New API 镜像
docker pull calciumion/new-api:latest

# 运行容器
docker run --name new-api -d --restart always -p 3000:3000 -e TZ=Asia/Shanghai -v /path/to/data:/data calciumion/new-api:latest
```

参数说明：
- `--name new-api`：设置容器名称
- `-d`：在后台运行容器
- `--restart always`：容器崩溃或系统重启时自动重启
- `-p 3000:3000`：将容器的 3000 端口映射到主机的 3000 端口
- `-e TZ=Asia/Shanghai`：设置时区为亚洲/上海
- `-v /path/to/data:/data`：将主机的 `/path/to/data` 目录挂载到容器的 `/data` 目录，用于持久化数据

### 方法二：使用 MySQL 数据库

如果您希望使用 MySQL 作为数据库而非默认的 SQLite：

```bash
docker run --name new-api -d --restart always -p 3000:3000 \
  -e SQL_DSN="root:password@tcp(mysql-host:3306)/oneapi" \
  -e TZ=Asia/Shanghai \
  -v /path/to/data:/data \
  calciumion/new-api:latest
```

### 方法三：使用自定义环境变量

您可以通过环境变量自定义 New API 的多种行为：

```bash
docker run --name new-api -d --restart always -p 3000:3000 \
  -e SQL_DSN="root:password@tcp(mysql-host:3306)/oneapi" \
  -e TZ=Asia/Shanghai \
  -e SESSION_SECRET="your-secret-key" \
  -e REDIS_CONN_STRING="redis://default:redispw@localhost:6379" \
  -e MEMORY_CACHE_ENABLED=true \
  -e GENERATE_DEFAULT_TOKEN=true \
  -v /path/to/data:/data \
  calciumion/new-api:latest
```

## 更新 New API

当有新版本发布时，您可以使用以下命令更新 New API：

```bash
# 拉取最新镜像
docker pull calciumion/new-api:latest

# 停止并删除旧容器
docker stop new-api
docker rm new-api

# 使用相同的参数启动新容器
docker run --name new-api -d --restart always -p 3000:3000 -e TZ=Asia/Shanghai -v /path/to/data:/data calciumion/new-api:latest
```

## 查看日志

您可以使用以下命令查看 New API 的日志：

```bash
docker logs new-api
# 实时查看日志
docker logs -f new-api
```

## 管理容器

```bash
# 停止容器
docker stop new-api

# 启动容器
docker start new-api

# 重启容器
docker restart new-api
```

## 访问 New API

安装完成后，您可以通过浏览器访问 `http://your-server-ip:3000` 进入管理面板。

默认管理员账号：`root`  
默认管理员密码：`123456`

## 故障排除

1. **无法访问服务**
   - 确认容器是否正在运行：`docker ps | grep new-api`
   - 检查端口映射：`docker port new-api`
   - 检查防火墙设置：确保 3000 端口已开放

2. **数据库连接问题**
   - 检查数据库连接字符串格式
   - 确保数据库服务可访问

3. **权限问题**
   - 检查挂载目录的权限：`ls -la /path/to/data`

## 下一步

- [配置渠道和模型](../user-guide/channel-configuration.md)
- [系统设置详解](../user-guide/system-settings.md)
- [API使用指南](../api-docs/introduction.md)
