---
hide:
  - footer
  - navigation
  - toc
---

<style>
  .md-typeset .grid.cards > ul {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 1rem;
    margin: 1.5em 0;
  }
  
  .md-typeset .grid.cards > ul > li {
    border: none;
    border-radius: 0.6rem;
    display: block;
    margin: 0;
    padding: 1.5em;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    color: white;
    position: relative;
    overflow: hidden;
    line-height: 1.5;
  }
  
  .md-typeset .grid.cards > ul > li:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
  }
  
  /* 添加柔和的暗色叠加，降低视觉冲击力 */
  .md-typeset .grid.cards > ul > li:after {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.12);
    pointer-events: none;
    z-index: 1;
  }
  
  /* 将内容提升到遮罩层之上 */
  .md-typeset .grid.cards > ul > li > * {
    position: relative;
    z-index: 2;
  }
  
  /* 降低饱和度的渐变色 */
  /* 第一部分的卡片颜色 */
  .md-typeset .grid.cards:nth-of-type(1) > ul > li:nth-child(1) {
    background: linear-gradient(135deg, rgba(65, 88, 208, 0.85), rgba(200, 80, 192, 0.85));
  }
  
  .md-typeset .grid.cards:nth-of-type(1) > ul > li:nth-child(2) {
    background: linear-gradient(135deg, rgba(0, 147, 233, 0.85), rgba(128, 208, 199, 0.85));
  }
  
  /* 修改快速指南的颜色，使其与快速安装区分开 */
  .md-typeset .grid.cards:nth-of-type(1) > ul > li:nth-child(3) {
    background: linear-gradient(135deg, rgba(255, 126, 95, 0.85), rgba(254, 180, 123, 0.85));
  }
  
  /* 第二部分的卡片颜色 */
  .md-typeset .grid.cards:nth-of-type(2) > ul > li:nth-child(1) {
    background: linear-gradient(135deg, rgba(255, 154, 139, 0.85), rgba(255, 106, 136, 0.85));
  }
  
  .md-typeset .grid.cards:nth-of-type(2) > ul > li:nth-child(2) {
    background: linear-gradient(135deg, rgba(8, 174, 234, 0.85), rgba(42, 245, 152, 0.85));
  }
  
  /* 修改用户指南的颜色，使渐变更加明显 */
  .md-typeset .grid.cards:nth-of-type(2) > ul > li:nth-child(3) {
    background: linear-gradient(135deg, rgba(114, 124, 245, 0.85), rgba(180, 52, 235, 0.85));
  }
  
  .md-typeset .grid.cards:nth-of-type(2) > ul > li:nth-child(4) {
    background: linear-gradient(135deg, rgba(250, 139, 255, 0.85), rgba(43, 210, 255, 0.85));
  }
  
  /* 修改帮助支持的颜色，改为绿色渐变 */
  .md-typeset .grid.cards:nth-of-type(2) > ul > li:nth-child(5) {
    background: linear-gradient(135deg, rgba(97, 184, 134, 0.85), rgba(10, 126, 88, 0.85));
  }
  
  /* 增加一个微妙的纹理背景，减轻视觉疲劳 */
  .md-typeset .grid.cards > ul > li {
    background-blend-mode: overlay;
    background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ffffff' fill-opacity='0.05' fill-rule='evenodd'%3E%3Cpath d='M0 38.59l2.83-2.83 1.41 1.41L1.41 40H0v-1.41zM0 1.4l2.83 2.83 1.41-1.41L1.41 0H0v1.41zM38.59 40l-2.83-2.83 1.41-1.41L40 38.59V40h-1.41zM40 1.41l-2.83 2.83-1.41-1.41L38.59 0H40v1.41zM20 18.6l2.83-2.83 1.41 1.41L21.41 20l2.83 2.83-1.41 1.41L20 21.41l-2.83 2.83-1.41-1.41L18.59 20l-2.83-2.83 1.41-1.41L20 18.59z'/%3E%3C/g%3E%3C/svg%3E");
  }
  
  .md-typeset .grid.cards > ul > li p {
    margin: 0.6em 0;
    color: rgba(255, 255, 255, 0.92);
    line-height: 1.6;
    font-size: 0.95em;
    letter-spacing: 0.01em;
  }
  
  .md-typeset .grid.cards > ul > li p strong,
  .md-typeset .grid.cards > ul > li strong {
    color: white;
    display: block;
    margin-top: 0.5em;
    font-size: 1.15em;
    font-weight: 600;
    letter-spacing: 0.01em;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  }
  
  .md-typeset .grid.cards > ul > li hr {
    margin: 0.9em 0;
    background-color: rgba(255, 255, 255, 0.2);
    border: none;
    height: 1px;
    opacity: 0.8;
  }
  
  .md-typeset .grid.cards > ul > li .twemoji {
    font-size: 2.6em;
    display: block;
    margin: 0 auto 0.6em;
    text-align: center;
    filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.15));
    transition: transform 0.2s ease;
  }
  
  .md-typeset .grid.cards > ul > li:hover .twemoji {
    transform: scale(1.05);
  }
  
  .md-typeset .grid.cards > ul > li .title {
    text-align: center;
    font-weight: bold;
    margin-bottom: 0.5em;
  }
  
  .md-typeset .grid.cards > ul > li .more-link {
    display: inline-flex;
    align-items: center;
    margin-top: 0.9em;
    color: white;
    background-color: rgba(255, 255, 255, 0.15);
    padding: 0.4em 1em;
    border-radius: 2em;
    transition: all 0.2s ease;
    font-weight: 500;
    font-size: 0.9em;
    letter-spacing: 0.02em;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  }
  
  .md-typeset .grid.cards > ul > li .more-link:hover {
    background-color: rgba(255, 255, 255, 0.25);
    text-decoration: none;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
    transform: translateX(3px);
  }
  
  /* 调整卡片内的链接文本颜色 */
  .md-typeset .grid.cards > ul > li a:not(.more-link) {
    color: white;
    text-decoration: underline;
    text-decoration-color: rgba(255, 255, 255, 0.3);
    text-decoration-thickness: 1px;
    text-underline-offset: 2px;
    transition: text-decoration-color 0.2s;
  }
  
  .md-typeset .grid.cards > ul > li a:not(.more-link):hover {
    text-decoration-color: rgba(255, 255, 255, 0.8);
  }

  /* 优化标题样式 */
  .md-typeset h1, .md-typeset h2 {
    font-weight: 600;
    color: var(--md-default-fg-color--light);
    margin-bottom: 0.8em;
  }
  
  .md-typeset h1 {
    font-size: 2.2em;
  }
  
  .md-typeset h2 {
    font-size: 1.6em;
  }
</style>

# 🚀 **开始使用**

## 🎯 **快速入门指南**

<div class="grid cards" markdown>

-   :material-server-network:{ .twemoji } 
    
    **快速安装**
    
    ---
    
    在服务器上部署 New API，快速搭建您的 AI 服务网关
    
    [了解更多 →](installation/quick-local-installation.md){ .more-link }

-   :material-api:{ .twemoji } 
    
    **快速调用**
    
    ---
    
    使用标准 OpenAI 格式接口，快速接入您的AI应用程序
    
    [了解更多 →](installation/quick-call.md){ .more-link }

-   :material-account-group:{ .twemoji } 
    
    **快速指南**
    
    ---
    
    图文并茂的方式带您快速了解 New API 的核心功能及使用方法
    
    [了解更多 →](installation/quick-guide.md){ .more-link }

</div>

## 📚 **浏览我们的文档**

<div class="grid cards" markdown>

-   :fontawesome-solid-book:{ .twemoji } 
    
    **维基百科**
    
    ---
    
    了解项目介绍、特性说明、技术架构和路线图
    
    [了解更多 →](wiki/project-introduction.md){ .more-link }

-   :fontawesome-solid-wrench:{ .twemoji } 
    
    **安装指南**
    
    ---
    
    快速入门、精细化安装和参数配置指南
    
    [了解更多 →](installation/quick-local-installation.md){ .more-link }

-   :fontawesome-solid-user:{ .twemoji } 
    
    **用户指南**
    
    ---
    
    详细的使用说明和最佳实践
    
    [了解更多 →](user-guide/i18n.md){ .more-link }

-   :fontawesome-solid-code:{ .twemoji } 
    
    **接口文档**
    
    ---
    
    全面的API接口说明和调用示例
    
    [了解更多 →](api-docs/interface-introduction.md){ .more-link }

-   :fontawesome-solid-headset:{ .twemoji } 
    
    **帮助支持**
    
    ---
    
    常见问题解答和技术支持渠道
    
    [了解更多 →](support/community-interaction.md){ .more-link }

</div>
