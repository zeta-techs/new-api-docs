# 快速本地安装指南

本文档将指导您如何在本地环境快速安装并运行 New API。

## 系统要求

- 操作系统：Windows、macOS 或 Linux
- Go 版本：1.20 或更高
- 数据库：SQLite（默认）或 MySQL（版本 >= 5.7.8）或 PostgreSQL（版本 >= 9.6）

## 从源码安装

### 1. 下载源码

```bash
git clone https://github.com/Calcium-Ion/new-api.git
cd new-api
```

### 2. 编译项目

```bash
go build -o new-api
```

### 3. 运行项目

```bash
./new-api --port 3000
```
或在 Windows 上：
```cmd
new-api.exe --port 3000
```

## 配置

可以通过环境变量或配置文件设置各种参数，比如：

```bash
export SQL_DSN="root:123456@tcp(localhost:3306)/oneapi"
export SESSION_SECRET="your-session-secret"
export REDIS_CONN_STRING="redis://localhost:6379"
```

## 访问服务

安装完成后，可以通过浏览器访问 `http://localhost:3000` 进入管理面板。

默认管理员账号：`root`  
默认管理员密码：`123456`

## 下一步

- 添加渠道和模型
- 创建用户和令牌
- 配置系统设置

更多高级配置，请参考[系统配置文档](../user-guide/system-configuration.md)。
