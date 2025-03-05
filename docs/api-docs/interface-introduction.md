---
hide:
  - footer
---

<style>
  .md-typeset .grid.cards > ul {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 1rem;
    margin: 1em 0;
  }
  
  .md-typeset .grid.cards > ul > li {
    border: none;
    border-radius: 0.8rem;
    box-shadow: var(--md-shadow-z2);
    padding: 1.5rem;
    transition: transform 0.25s, box-shadow 0.25s;
    background: linear-gradient(135deg, var(--md-primary-fg-color), var(--md-accent-fg-color));
    color: var(--md-primary-bg-color);
  }

  .md-typeset .grid.cards > ul > li:hover {
    transform: scale(1.02);
    box-shadow: var(--md-shadow-z3);
  }

  .md-typeset .grid.cards > ul > li > hr {
    margin: 0.8rem 0;
    border: none;
    border-bottom: 2px solid var(--md-primary-bg-color);
    opacity: 0.2;
  }

  .md-typeset .grid.cards > ul > li > p {
    margin: 0.5rem 0;
  }

  .md-typeset .grid.cards > ul > li > p > em {
    color: var(--md-primary-bg-color);
    opacity: 0.8;
    font-style: normal;
  }

  .md-typeset .grid.cards > ul > li > p > .twemoji {
    font-size: 2.5rem;
    display: block;
    margin: 0.5rem auto;
  }

  /* 新增：美化介绍部分 */
  .interface-intro {
    margin: 2rem 0;
    padding: 1.5rem;
    border-radius: 0.8rem;
    background-color: var(--md-primary-fg-color--light);
    color: var(--md-primary-bg-color);
  }

  /* 新增：优化卡片链接样式 */
  .md-typeset .grid.cards > ul > li a {
    display: inline-block;
    padding: 0.4rem 1.2rem;
    margin-top: 0.6rem;
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 2rem;
    color: var(--md-primary-bg-color);
    font-weight: 500;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .md-typeset .grid.cards > ul > li a:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateX(0.2rem);
  }

  .md-typeset .grid.cards > ul > li a::after {
    content: " →";
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .md-typeset .grid.cards > ul > li a:hover::after {
    opacity: 1;
  }
</style>

# 接口总览

## 💫 中继接口

<div class="grid cards" markdown>

-   :material-chat:{ .twemoji }

    **聊天（Chat）**

    ---

    支持多种主流聊天模型格式：
    
    - OpenAI Chat Completions
    - Anthropic Messages
    - Deepseek Reasoning Chat

    [查看详情 →](openai-chat.md)

-   :material-alphabetical:{ .twemoji }

    **嵌入（Embeddings）**

    ---

    文本向量嵌入服务：
    
    - OpenAI Embeddings 格式

    [查看详情 →](openai-embedding.md)

-   :material-swap-vertical:{ .twemoji }

    **重排序（Rerank）**

    ---

    搜索结果重排序服务：
    
    - Jina AI Rerank
    - Cohere Rerank

    [查看详情 →](jinaai-rerank.md)

-   :material-lightning-bolt:{ .twemoji }

    **实时对话（Realtime）**

    ---

    支持流式实时对话：
    
    - OpenAI 流式输出格式

    [查看详情 →](openai-realtime.md)

-   :material-image:{ .twemoji }

    **图像（Image）**

    ---

    AI 图像生成服务：
    
    - OpenAI DALL·E
    - Midjourney Proxy/Plus

    [查看详情 →](openai-image.md)

-   :material-volume-high:{ .twemoji }

    **音频（Audio）**

    ---

    语音相关服务：
    
    - OpenAI 音频格式

    [查看详情 →](openai-audio.md)

-   :material-music:{ .twemoji }

    **音乐（Music）**

    ---

    AI 音乐生成服务：
    
    - Suno API 格式

    [查看详情 →](suno-music.md)

</div>

## 🖥️ 前端接口

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .twemoji }

    **即将推出**

    ---

    前端接口文档正在码字中，敬请期待！
    
    [了解更多 →](../coming-soon.md)

</div>

---

## 📖 接口说明

!!! abstract "接口类型"
    New API 提供两大类接口：
    
    1. **中继接口**：用于 AI 模型的调用，支持多种主流模型格式
    2. **前端接口**：用于支持 Web 界面的功能调用，提供完整的前端功能支持

!!! tip "功能支持标识"
    在接口文档中，我们使用以下图标来标识功能支持状态：

    - ✅ **已支持**：该功能已经完全实现并可以使用
    - ❌ **未支持**：该功能正在开发中或计划开发

!!! example "快速开始"
    1. 浏览上方卡片选择需要使用的接口
    2. 点击对应卡片的"查看详情"了解具体用法
    3. 按照文档说明进行接口调用 