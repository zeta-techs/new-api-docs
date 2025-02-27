# New API 快速入门指南

本指南将帮助您快速上手 New API，从安装到基本使用仅需几步。

## 部署选项

New API 提供多种部署方式，选择最适合您的：

1. **Docker 部署**（最简单）：
   ```bash
   docker run --name new-api -d --restart always -p 3000:3000 -e TZ=Asia/Shanghai -v /path/to/data:/data calciumion/new-api:latest
   ```

2. **Docker Compose 部署**（推荐）：
   ```bash
   git clone https://github.com/Calcium-Ion/new-api.git
   cd new-api
   docker-compose up -d
   ```

3. **宝塔面板部署**：
   在宝塔面板的应用商店中搜索并安装 **New-API**

4. **源码部署**：
   详见 [快速本地安装](./quick-local-installation.md)

## 初始配置

1. 访问管理面板：`http://your-server-ip:3000`
2. 使用默认账号登录：
   - 用户名：`root`
   - 密码：`123456`
3. 首次登录后请立即修改默认密码！

## 添加渠道

1. 在左侧菜单选择"渠道管理"
2. 点击"新建"按钮
3. 选择渠道类型（如 OpenAI、Anthropic、Gemini 等）
4. 填写渠道信息和密钥
5. 设置权重和优先级
6. 保存设置

## 创建令牌

1. 在左侧菜单选择"令牌管理"
2. 点击"新建"按钮
3. 设置令牌名称、额度和可用模型
4. 复制生成的令牌字符串

## 开始使用

现在您可以使用创建的令牌通过 API 调用各种模型，例如：

```bash
curl https://your-server-ip:3000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好！"}]
  }'
```

更多 API 调用示例请参考 [快速调用指南](./quick-call.md)。

## 后续步骤

- 配置系统设置
- 添加更多渠道和模型
- 探索高级功能如模型权重、限流和监控

## 需要帮助？

如有问题，请查看 [常见问题](../support/faq.md) 或加入我们的 [社区交流群](../support/community-interaction.md)。
