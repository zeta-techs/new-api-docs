# 部署指南

## 部署要求

- 本地数据库（默认）：SQLite（Docker 部署默认使用 SQLite，必须挂载 `/data` 目录到宿主机）
- 远程数据库：MySQL 版本 >= 5.7.8，PgSQL 版本 >= 9.6

## Docker部署

!!! tip
    最新版Docker镜像：`calciumion/new-api:latest`  
    默认账号root 密码123456

### 多机部署注意事项
- 必须设置环境变量 `SESSION_SECRET`，否则会导致多机部署时登录状态不一致。
- 如果公用Redis，必须设置 `CRYPTO_SECRET`，否则会导致多机部署时Redis内容无法获取。

### 使用 Docker Compose 部署（推荐）

1. 下载项目:
```shell
# 下载项目
git clone https://github.com/Calcium-Ion/new-api.git
cd new-api

# 按需编辑 docker-compose.yml
# nano docker-compose.yml
# vim docker-compose.yml

# 启动
docker-compose up -d
```

#### 更新版本
```shell
docker-compose pull
docker-compose up -d
```

### 直接使用 Docker 镜像

```shell
# 使用 SQLite 的部署命令：
docker run --name new-api -d --restart always -p 3000:3000 -e TZ=Asia/Shanghai -v /home/ubuntu/data/new-api:/data calciumion/new-api:latest

# 使用 MySQL 的部署命令，在上面的基础上添加 -e SQL_DSN="root:123456@tcp(localhost:3306)/oneapi"，请自行修改数据库连接参数。
# 例如：
docker run --name new-api -d --restart always -p 3000:3000 -e SQL_DSN="root:123456@tcp(localhost:3306)/oneapi" -e TZ=Asia/Shanghai -v /home/ubuntu/data/new-api:/data calciumion/new-api:latest
```

#### 更新版本
```shell
# 拉取最新镜像
docker pull calciumion/new-api:latest
# 停止并删除旧容器
docker stop new-api
docker rm new-api
# 使用相同参数运行新容器
docker run --name new-api -d --restart always -p 3000:3000 -e TZ=Asia/Shanghai -v /home/ubuntu/data/new-api:/data calciumion/new-api:latest
```

或者使用 Watchtower 自动更新（不推荐，可能会导致数据库不兼容）：
```shell
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock containrrr/watchtower -cR
``` 