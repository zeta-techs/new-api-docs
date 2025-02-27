# 宝塔面板安装 New API 指南

本指南详细介绍如何使用宝塔面板安装 New API。宝塔面板提供了图形化界面，使得安装和管理 New API 变得简单。

## 前提条件

- 一台安装了宝塔面板的服务器（支持 Linux 系统）
- 宝塔面板版本 >= 9.2.0
- 服务器至少 1GB 内存（推荐 2GB 或更多）

## 宝塔面板安装步骤

如果您尚未安装宝塔面板，请按照以下步骤进行安装：

### 安装宝塔面板（Linux）

```bash
# Centos
yum install -y wget && wget -O install.sh https://download.bt.cn/install/install_6.0.sh && sh install.sh

# Ubuntu/Debian
wget -O install.sh https://download.bt.cn/install/install-ubuntu_6.0.sh && sudo bash install.sh
```

安装完成后，面板会显示访问地址、用户名和密码，请妥善保管。

## 通过宝塔面板安装 New API

### 步骤 1：安装 Docker 管理器

1. 登录宝塔面板
2. 点击左侧菜单的【软件商店】
3. 搜索【Docker】并安装【Docker 管理器】
4. 安装完成后，Docker 管理器会出现在左侧菜单中

### 步骤 2：安装 New API

1. 点击左侧菜单的【Docker】进入 Docker 管理器
2. 点击【应用商店】选项卡
3. 搜索【New-API】或【New API】
4. 点击【安装】按钮

![宝塔Docker应用商店截图](../assets/images/bt-docker-store.png)

### 步骤 3：配置 New API

安装时需要配置以下选项：

1. **容器名称**：可以保持默认或自定义
2. **映射端口**：默认为 3000，可以根据需要修改
3. **数据目录**：保存 New API 数据的目录，建议修改为更好记的位置，如 `/www/wwwroot/new-api-data`
4. **环境变量**：可以设置以下常用环境变量
   - `TZ=Asia/Shanghai`：设置时区
   - `SQL_DSN`：如果使用外部 MySQL，可以设置数据库连接字符串
   - `SESSION_SECRET`：设置会话密钥
   - `REDIS_CONN_STRING`：如果使用 Redis，可以设置连接字符串

![宝塔安装配置截图](../assets/images/bt-docker-config.png)

5. 点击【提交】按钮完成安装

### 步骤 4：配置反向代理（可选，但推荐）

如果您希望通过域名访问 New API，可以配置反向代理：

1. 在宝塔面板中，点击【网站】
2. 添加新站点或选择现有站点
3. 点击【设置】->【反向代理】
4. 添加新的反向代理：
   - 名称：自定义，如 New API
   - 目标 URL：`http://127.0.0.1:3000`（如果您修改了端口，请对应修改）
   - 点击【提交】保存设置

![宝塔反向代理配置截图](../assets/images/bt-reverse-proxy.png)

### 步骤 5：设置 SSL（可选，但推荐）

为您的站点启用 HTTPS 提高安全性：

1. 在站点设置中，点击【SSL】
2. 选择【Let's Encrypt】自动申请免费证书
3. 选择要签发的域名，点击【申请】
4. 证书申请成功后，点击【强制 HTTPS】

## 访问 New API

安装完成后，您可以通过以下方式访问 New API：

- 直接访问：`http://your-server-ip:3000`
- 通过反向代理和域名：`https://your-domain.com`

默认管理员账号：`root`  
默认管理员密码：`123456`

## 管理 New API 容器

在宝塔面板的 Docker 管理器中，您可以轻松管理 New API 容器：

1. 点击左侧【Docker】菜单
2. 在【容器列表】中找到 New API 容器
3. 可以执行以下操作：
   - 启动/停止/重启容器
   - 查看容器日志
   - 更新容器
   - 修改容器配置

## 常见问题及解决方法

1. **安装后无法访问 New API**
   - 检查 Docker 容器是否正常运行
   - 检查端口是否被占用或被防火墙阻止
   - 查看容器日志是否有错误信息

2. **数据库连接错误**
   - 检查 SQL_DSN 环境变量格式是否正确
   - 确保数据库服务器允许远程连接
   - 检查数据库用户权限

3. **更新 New API**
   - 在 Docker 管理器中，选择容器，点击【更新】按钮
   - 拉取最新镜像后重建容器

4. **备份数据**
   - 定期备份 `/data` 目录（您在安装时设置的数据目录）
   - 如使用 MySQL，请同时备份数据库

## 相关资源

- [宝塔面板官网](https://www.bt.cn)
- [New API GitHub 仓库](https://github.com/Calcium-Ion/new-api)
- [New API 使用文档](../user-guide/getting-started.md)
