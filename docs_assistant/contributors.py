import os
import logging
from datetime import datetime
from github_api import fetch_github_data, GITHUB_REPO, GITHUB_PROXY, USE_PROXY
from utils import update_markdown_file, DOCS_DIR

logger = logging.getLogger('contributors')

def format_contributors_markdown(contributors_data):
    """将贡献者数据格式化为Markdown内容"""
    if not contributors_data or len(contributors_data) == 0:
        return "暂无贡献者数据，请稍后再试。"
    
    # 生成Markdown格式的贡献者列表
    markdown = ""
    
    # 为每个贡献者创建信息卡片
    for index, contributor in enumerate(contributors_data):
        username = contributor.get('login', '未知用户')
        avatar_url = contributor.get('avatar_url', '')
        # 替换头像URL为代理URL
        if USE_PROXY and 'githubusercontent.com' in avatar_url:
            avatar_url = f'{GITHUB_PROXY}?url={avatar_url}'
        profile_url = contributor.get('html_url', '')
        # 替换个人主页URL为代理URL
        if USE_PROXY and 'github.com' in profile_url:
            profile_url = f'{GITHUB_PROXY}?url={profile_url}'
        contributions = contributor.get('contributions', 0)
        
        # 获取前三名的特殊样式
        medal_class = ""
        medal_label = ""
        if index == 0:
            medal_class = "gold-medal"
            medal_label = '<span class="medal-rank rank-1">1</span>'
        elif index == 1:
            medal_class = "silver-medal"
            medal_label = '<span class="medal-rank rank-2">2</span>'
        elif index == 2:
            medal_class = "bronze-medal"
            medal_label = '<span class="medal-rank rank-3">3</span>'
        
        # 三级标题 + 简要介绍
        markdown += f'### {username}\n\n'
        markdown += f'<div class="contributor-simple {medal_class}">\n'
        markdown += f'  <div class="avatar-container">\n'
        markdown += f'    <img src="{avatar_url}" alt="{username}" class="contributor-avatar" />\n'
        if medal_label:
            markdown += f'    {medal_label}\n'
        markdown += f'  </div>\n'
        markdown += f'  <div class="contributor-details">\n'
        markdown += f'    <a href="{profile_url}" target="_blank">{username}</a>\n'
        markdown += f'    <span class="contributor-stats">贡献次数: {contributions}</span>\n'
        markdown += f'  </div>\n'
        markdown += f'</div>\n\n'
        markdown += '---\n\n'
    
    # 添加简洁的CSS样式
    markdown += '''
<style>
.contributor-simple {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.avatar-container {
    position: relative;
    margin-right: 15px;
}

.contributor-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
}

.medal-rank {
    position: absolute;
    bottom: -5px;
    right: -5px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 12px;
    color: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.rank-1 {
    background-color: #ffd700;
}

.rank-2 {
    background-color: #c0c0c0;
}

.rank-3 {
    background-color: #cd7f32;
}

.gold-medal .contributor-avatar {
    border: 4px solid #ffd700;
    box-shadow: 0 0 10px #ffd700;
}

.silver-medal .contributor-avatar {
    border: 4px solid #c0c0c0;
    box-shadow: 0 0 10px #c0c0c0;
}

.bronze-medal .contributor-avatar {
    border: 4px solid #cd7f32;
    box-shadow: 0 0 10px #cd7f32;
}

.contributor-details {
    display: flex;
    flex-direction: column;
}

.contributor-details a {
    font-weight: 500;
    text-decoration: none;
}

.contributor-stats {
    font-size: 0.9rem;
    color: #666;
}

[data-md-color-scheme="slate"] .contributor-stats {
    color: #aaa;
}
</style>
'''
    
    return markdown

def update_special_thanks_file():
    """更新特别感谢文件"""
    try:
        # 获取贡献者数据
        contributors_data, success = fetch_github_data(GITHUB_REPO, "contributors", 50)
        if not success or not contributors_data:
            logger.error("无法获取贡献者数据")
            return False
        
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 格式化为Markdown
        base_content = f"""# 🙏特别鸣谢\n\n

New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。

## 👨‍💻 开发贡献者

以下是所有为项目做出贡献的开发者列表。在此感谢他们的辛勤工作和创意！

!!! info "贡献者信息（数据更新于: {current_time}）"
    以下贡献者数据从 [GitHub Contributors 页面](https://github.com/Calcium-Ion/new-api/graphs/contributors) 自动获取前50名。贡献度前三名分别以金、银、铜牌边框标识。如果您也想为项目做出贡献，欢迎提交 Pull Request。

"""
        contributors_markdown = format_contributors_markdown(contributors_data)
        full_content = base_content + contributors_markdown
        
        # 更新文件
        thanks_file = os.path.join(DOCS_DIR, 'docs/wiki/special-thanks.md')
        return update_markdown_file(thanks_file, full_content)
    
    except Exception as e:
        logger.error(f"更新贡献者列表失败: {str(e)}")
        return False