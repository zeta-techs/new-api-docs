# 🐙 Docker Compose 安装指南

本文档提供了使用Docker Compose部署New API的详细步骤。

## 📋 前置要求

- 已安装Docker和Docker Compose
- 推荐系统: Linux (Ubuntu/CentOS/Debian等)

## 🔄 使用Docker Compose部署

### 📂 方法一：使用Git克隆项目（推荐）

如果您能够正常访问GitHub，推荐使用此方法：

```shell
# 下载项目源码
git clone https://github.com/Calcium-Ion/new-api.git

# 进入项目目录
cd new-api
```

### ✍️ 方法二：手动创建配置文件

如果无法访问GitHub或克隆仓库，可以手动创建配置文件：

1. 创建一个目录用于New API部署：

```shell
mkdir new-api
cd new-api
```

2. 在该目录中创建`docker-compose.yml`文件

   您可以参考[Docker Compose配置说明](docker-compose-yml.md)文档中的配置示例，根据您的需求选择：
   
   - 生产环境推荐使用完整配置（包含MySQL和Redis）
   - 测试环境可以使用简化配置

3. 使用文本编辑器创建文件：

```shell
# 使用nano编辑器
nano docker-compose.yml

# 或使用vim编辑器
vim docker-compose.yml
```

将选择的配置内容复制到该文件中，并根据需要进行自定义修改。

## 🚀 启动服务

配置文件准备好后，无论您是通过Git克隆还是手动创建，都可以使用以下命令启动服务：

```shell
# 使用Docker Compose启动服务
docker compose up -d
```

该命令会自动拉取所需镜像并在后台启动服务。

## 📋 查看日志

```shell
# 查看服务日志
docker compose logs -f
```

## 🛑 停止服务

```shell
# 停止服务
docker compose down
```

## 🌐 访问系统

服务启动成功后，访问`http://服务器IP:3000`即可进入系统。

默认管理员账号: `root`  
默认管理员密码: `123456`

!!! danger "重要"
    建议首次登录后立即修改默认密码。
