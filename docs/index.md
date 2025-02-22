# New API

<div align="center">
<img src="/web/public/logo.png" alt="new-api logo"/>

🍥新一代大模型网关与AI资产管理系统

[![license](https://img.shields.io/github/license/Calcium-Ion/new-api?color=brightgreen)](https://raw.githubusercontent.com/Calcium-Ion/new-api/main/LICENSE)
[![release](https://img.shields.io/github/v/release/Calcium-Ion/new-api?color=brightgreen&include_prereleases)](https://github.com/Calcium-Ion/new-api/releases/latest)
[![docker](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/users/Calcium-Ion/packages/container/package/new-api)
[![docker](https://img.shields.io/badge/docker-dockerHub-blue)](https://hub.docker.com/r/CalciumIon/new-api)
[![GoReportCard](https://goreportcard.com/badge/github.com/Calcium-Ion/new-api)](https://goreportcard.com/report/github.com/Calcium-Ion/new-api)
</div>

## 项目说明

!!! note
    本项目为开源项目，在[One API](https://github.com/songquanpeng/one-api)的基础上进行二次开发

!!! important
    - 使用者必须在遵循 OpenAI 的[使用条款](https://openai.com/policies/terms-of-use)以及**法律法规**的情况下使用，不得用于非法用途。
    - 本项目仅供个人学习使用，不保证稳定性，且不提供任何技术支持。
    - 根据[《生成式人工智能服务管理暂行办法》](http://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)的要求，请勿对中国地区公众提供一切未经备案的生成式人工智能服务。

## 主要特性

1. 🎨 全新的UI界面（部分界面还待更新）
2. 🌍 多语言支持（待完善）
3. 🎨 添加Midjourney-Proxy(Plus)接口支持
4. 💰 支持在线充值功能（易支付）
5. 🔍 支持用key查询使用额度
6. 📑 分页支持选择每页显示数量
7. 🔄 兼容原版One API的数据库
8. 💵 支持模型按次数收费
9. ⚖️ 支持渠道加权随机
10. 📈 数据看板（控制台）
11. 🔒 可设置令牌能调用的模型
12. 🤖 支持Telegram授权登录
13. 🎵 添加Suno API接口支持
14. 🔄 支持Rerank模型
15. ⚡ 支持OpenAI Realtime API
16. 支持使用路由/chat2link进入聊天界面
17. 🧠 支持通过模型名称后缀设置reasoning effort

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Calcium-Ion/new-api&type=Date)](https://star-history.com/#Calcium-Ion/new-api&Date)

## 界面预览

<div class="image-grid">
    <div class="image-item">
        <img src="https://github.com/user-attachments/assets/a0dcd349-5df8-4dc8-9acf-ca272b239919" alt="控制台界面">
        <p>控制台界面</p>
    </div>
    <div class="image-item">
        <img src="https://github.com/user-attachments/assets/c7d0f7e1-729c-43e2-ac7c-2cb73b0afc8e" alt="渠道管理界面">
        <p>渠道管理界面</p>
    </div>
    <div class="image-item">
        <img src="https://github.com/user-attachments/assets/29f81de5-33fc-4fc5-a5ff-f9b54b653c7c" alt="令牌管理界面">
        <p>令牌管理界面</p>
    </div>
    <div class="image-item">
        <img src="https://github.com/user-attachments/assets/4fa53e18-d2c5-477a-9b26-b86e44c71e35" alt="系统设置界面">
        <p>系统设置界面</p>
    </div>
</div>

<style>
.image-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin: 20px 0;
}
.image-item {
    text-align: center;
}
.image-item img {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.image-item p {
    margin-top: 8px;
    color: #666;
}
</style>
