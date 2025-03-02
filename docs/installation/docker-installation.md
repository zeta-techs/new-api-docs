# 🐳 Docker安装指南

本文档提供了使用Docker部署New API的详细步骤。

## 📋 基本要求

- 已安装Docker环境
- 推荐系统: Linux (Ubuntu/CentOS/Debian等)
- 端口: 默认使用3000端口

## 🚢 直接使用Docker镜像部署

### 💾 使用SQLite数据库（推荐新手）

```shell
docker run --name new-api -d --restart always \
  -p 3000:3000 \
  -e TZ=Asia/Shanghai \
  -v /your/data/path:/data \
  calciumion/new-api:latest
```

!!! warning "注意"
    请将 `/your/data/path` 替换为您想要存储数据的本地路径。

### 🗄️ 使用MySQL数据库

```shell
docker run --name new-api -d --restart always \
  -p 3000:3000 \
  -e SQL_DSN="用户名:密码@tcp(数据库地址:3306)/数据库名" \
  -e TZ=Asia/Shanghai \
  -v /your/data/path:/data \
  calciumion/new-api:latest
```

!!! warning "注意"
    请替换参数中的数据库连接信息。

## 🌐 访问系统

部署完成后，访问 `http://服务器IP:3000` 即可进入系统。

默认管理员账号: `root`  
默认管理员密码: `123456`

!!! danger "重要"
    建议首次登录后立即修改默认密码。
