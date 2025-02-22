# 相关项目

## 🌟 核心项目

### One API
[![One API](https://img.shields.io/github/stars/songquanpeng/one-api?style=social)](https://github.com/songquanpeng/one-api)

本项目基于 One API 进行二次开发，主要改进：

- 🎨 全新的UI界面设计
- 🌍 多语言国际化支持
- 💰 在线充值功能集成
- 🔄 渠道负载均衡优化
- 📊 数据统计看板
- 🤖 更多模型支持

## 🛠️ 推荐工具

### Docker 相关

=== "Watchtower"
    [![Watchtower](https://img.shields.io/docker/pulls/containrrr/watchtower?style=flat-square)](https://github.com/containrrr/watchtower)

    自动更新 Docker 容器：
    ```bash
    docker run -d \
      --name watchtower \
      -v /var/run/docker.sock:/var/run/docker.sock \
      containrrr/watchtower \
      --cleanup \
      --interval 86400
    ```

=== "Portainer"
    [![Portainer](https://img.shields.io/docker/pulls/portainer/portainer-ce?style=flat-square)](https://github.com/portainer/portainer)

    Docker可视化管理：
    ```bash
    docker run -d \
      --name portainer \
      -p 9000:9000 \
      -v /var/run/docker.sock:/var/run/docker.sock \
      -v portainer_data:/data \
      portainer/portainer-ce
    ```

### 缓存服务

=== "Redis"
    [![Redis](https://img.shields.io/docker/pulls/redis?style=flat-square)](https://redis.io/)

    推荐配置：
    ```bash
    docker run -d \
      --name redis \
      -p 6379:6379 \
      -v redis_data:/data \
      redis:alpine \
      redis-server --appendonly yes
    ```

=== "Memcached"
    [![Memcached](https://img.shields.io/docker/pulls/memcached?style=flat-square)](https://memcached.org/)

    适用于简单缓存：
    ```bash
    docker run -d \
      --name memcached \
      -p 11211:11211 \
      memcached:alpine
    ```

### 监控工具

=== "Prometheus"
    [![Prometheus](https://img.shields.io/docker/pulls/prom/prometheus?style=flat-square)](https://prometheus.io/)

    指标收集：
    ```yaml
    global:
      scrape_interval: 15s
    
    scrape_configs:
      - job_name: 'new-api'
        static_configs:
          - targets: ['localhost:3000']
    ```

=== "Grafana"
    [![Grafana](https://img.shields.io/docker/pulls/grafana/grafana?style=flat-square)](https://grafana.com/)

    可视化面板：
    ```bash
    docker run -d \
      --name grafana \
      -p 3000:3000 \
      grafana/grafana
    ```

## 🔧 开发工具

### API 测试

=== "Postman"
    [![Postman](https://img.shields.io/badge/Postman-FF6C37?style=flat-square&logo=postman&logoColor=white)](https://www.postman.com/)

    - API 调试和测试
    - 自动化测试
    - 团队协作
    - [示例集合下载](https://example.com/postman-collection)

=== "Insomnia"
    [![Insomnia](https://img.shields.io/badge/Insomnia-5849BE?style=flat-square&logo=insomnia&logoColor=white)](https://insomnia.rest/)

    - 开源替代方案
    - 支持 GraphQL
    - 设计简洁
    - [配置模板下载](https://example.com/insomnia-config)

## 📚 学习资源

### 文档工具

=== "MkDocs"
    [![MkDocs](https://img.shields.io/pypi/v/mkdocs?style=flat-square)](https://www.mkdocs.org/)

    本文档使用的生成工具：
    ```bash
    # 安装
    pip install mkdocs-material

    # 本地预览
    mkdocs serve

    # 构建静态文件
    mkdocs build
    ```

=== "VitePress"
    [![VitePress](https://img.shields.io/npm/v/vitepress?style=flat-square)](https://vitepress.dev/)

    Vue 驱动的静态网站生成器：
    ```bash
    # 安装
    npm install -D vitepress

    # 开发
    npm run docs:dev

    # 构建
    npm run docs:build
    ```

## 💡 最佳实践

1. 容器编排
   - 使用 Docker Compose
   - 配置健康检查
   - 实现自动重启

2. 监控告警
   - 设置指标采集
   - 配置告警规则
   - 通知集成

3. 日志管理
   - 集中式日志
   - 日志轮转
   - 异常监控

4. 安全加固
   - 容器安全
   - 网络隔离
   - 访问控制

!!! tip "工具选择建议"
    1. 根据实际需求选择合适的工具
    2. 优先考虑开源且活跃的项目
    3. 注意工具的维护状态
    4. 评估学习成本和社区支持 