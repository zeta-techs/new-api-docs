import os
import json
import time
import requests
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docs-updater')

# 环境变量配置
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 1800))  # 默认30分钟
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'Calcium-Ion/new-api')
GITHUB_PROXY = os.environ.get('GITHUB_PROXY', 'https://api2.aimage.cc/proxy')
USE_PROXY = os.environ.get('USE_PROXY', 'true').lower() == 'true'
DOCS_DIR = os.environ.get('DOCS_DIR', '/app/docs')

# GitHub API限制相关参数
MAX_RETRY_ATTEMPTS = 3
RATE_LIMIT_WAIT_TIME = 60  # 触发限制后等待的秒数

def fetch_github_data(repo, data_type, count, use_proxy=True):
    """获取GitHub数据，智能处理API限制，参数：
    repo: GitHub仓库 (例如："username/repo")
    data_type: 数据类型 ("releases" 或 "contributors")
    count: 最大获取数量
    use_proxy: 是否使用代理
    """
    logger.info(f"获取GitHub数据: {repo}, {data_type}, count={count}")
    
    headers = {'User-Agent': 'Mozilla/5.0 DocUpdater/1.0'}
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            # 构建API路径
            if data_type == "releases":
                api_path = f'repos/{repo}/releases?per_page={count}'
            elif data_type == "contributors":
                api_path = f'repos/{repo}/contributors?per_page={count}'
            else:
                return None, False
            
            # 构建API URL
            if use_proxy and USE_PROXY:
                original_api_url = f'https://api.github.com/{api_path}'
                api_url = f'{GITHUB_PROXY}?url={original_api_url}'
            else:
                api_url = f'https://api.github.com/{api_path}'
            
            # 发送请求
            response = requests.get(api_url, headers=headers, timeout=30)
            
            # 检查API限制
            if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
                logger.warning(f"GitHub API限制已达到，等待{RATE_LIMIT_WAIT_TIME}秒后重试...")
                time.sleep(RATE_LIMIT_WAIT_TIME)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            # 处理分页 (仅适用于贡献者数据)
            if data_type == "contributors" and len(data) < count and len(data) > 0:
                all_data = data.copy()
                page = 2
                
                # 最多获取3页，避免触发API限制
                while len(all_data) < count and page <= 3:
                    # 等待1秒避免请求过快
                    time.sleep(1)
                    
                    # 构建下一页URL
                    next_api_url = f'{api_path}&page={page}'
                    if use_proxy and USE_PROXY:
                        next_url = f'{GITHUB_PROXY}?url=https://api.github.com/{next_api_url}'
                    else:
                        next_url = f'https://api.github.com/{next_api_url}'
                    
                    next_response = requests.get(next_url, headers=headers, timeout=30)
                    next_response.raise_for_status()
                    next_data = next_response.json()
                    
                    if not next_data:
                        break
                        
                    all_data.extend(next_data)
                    page += 1
                
                return all_data[:count], True
            
            return data, True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败 (尝试 {attempt+1}/{MAX_RETRY_ATTEMPTS}): {str(e)}")
            
            # 如果代理失败，尝试直接访问
            if use_proxy and USE_PROXY and attempt == 0:
                logger.info("代理请求失败，尝试直接访问")
                return fetch_github_data(repo, data_type, count, False)
            
            # 等待后重试
            time.sleep(5)
            
    logger.error(f"在{MAX_RETRY_ATTEMPTS}次尝试后获取数据失败")
    return None, False

def format_file_size(bytes):
    """格式化文件大小"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes/1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes/(1024*1024):.2f} MB"
    else:
        return f"{bytes/(1024*1024*1024):.2f} GB"

def format_contributors_markdown(contributors_data):
    """将贡献者数据格式化为Markdown内容 - 简化版"""
    if not contributors_data or len(contributors_data) == 0:
        return "暂无贡献者数据，请稍后再试。"
    
    # 生成Markdown格式的贡献者列表
    markdown = ""
    
    # 添加数据更新信息
    markdown += f'!!! note "数据信息"\n'
    markdown += f'    数据更新于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
    
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

def format_releases_markdown(releases_data):
    """将发布数据格式化为Markdown内容 - 简化版"""
    if not releases_data or len(releases_data) == 0:
        return "暂无版本数据，请稍后再试。"
    
    markdown = "# 📝 更新日志\n\n"
    markdown += "!!! warning \"更多版本\"\n"
    markdown += f"    如需查看全部历史版本，请访问 [GitHub Releases 页面](https://github.com/{GITHUB_REPO}/releases)，本页面从该页面定时获取最新更新信息。\n\n"
    
    # 添加数据更新信息
    markdown += f'!!! note "数据信息"\n'
    markdown += f'    数据更新于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n'
    
    for index, release in enumerate(releases_data):
        tag_name = release.get('tag_name', '未知版本')
        name = release.get('name') or tag_name
        published_at = release.get('published_at', '')
        body = release.get('body', '无发布说明')
        prerelease = release.get('prerelease', False)
        
        if published_at:
            try:
                # 转换ISO格式的时间为更友好的格式
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = pub_date.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                formatted_date = published_at
        else:
            formatted_date = '未知时间'
        
        # 处理Markdown格式
        body = body.replace('### ', '#### ').replace('## ', '### ')
        
        # 替换图片链接（如果使用代理）
        if USE_PROXY:
            import re
            # 替换Markdown格式的图片链接
            body = re.sub(r'!\[(.*?)\]\((https?://[^)]+)\)', 
                          f'![\g<1>]({GITHUB_PROXY}?url=\\2)', 
                          body)
            
            # 替换HTML格式的图片链接
            body = re.sub(r'<img([^>]*)src="(https?://[^"]+)"([^>]*)>', 
                          f'<img\\1src="{GITHUB_PROXY}?url=\\2"\\3>', 
                          body)
        
        markdown += f'## {name}\n\n'
        
        # 版本类型标签
        version_type = "预发布版本" if prerelease else "正式版本"
        if index == 0:
            version_type = f"最新{version_type}"
            admonition_type = "success"
        else:
            admonition_type = "info"
        
        markdown += f'???+ {admonition_type} "{version_type} · 发布于 {formatted_date}"\n\n'
        
        # 缩进内容以适应admonition格式
        indented_body = '\n'.join(['    ' + line for line in body.split('\n')])
        markdown += f'{indented_body}\n\n'
        
        # 添加资源下载部分
        assets = release.get('assets', [])
        if assets or tag_name:
            markdown += '    **下载资源**\n\n'
            # 添加正常资源
            for asset in assets:
                name = asset.get('name', '')
                url = asset.get('browser_download_url', '')
                # 替换下载URL为代理URL
                if USE_PROXY and 'github.com' in url:
                    url = f'{GITHUB_PROXY}?url={url}'
                size = format_file_size(asset.get('size', 0))
                markdown += f'    - [{name}]({url}) ({size})\n'
            
            # 添加源代码下载链接
            if tag_name:
                # 构建zip下载链接
                zip_url = f'https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag_name}.zip'
                if USE_PROXY:
                    proxy_zip_url = f'{GITHUB_PROXY}?url={zip_url}'
                    markdown += f'    - [Source code (zip)]({proxy_zip_url})\n'
                else:
                    markdown += f'    - [Source code (zip)]({zip_url})\n'
                
                # 构建tar.gz下载链接
                tar_url = f'https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag_name}.tar.gz'
                if USE_PROXY:
                    proxy_tar_url = f'{GITHUB_PROXY}?url={tar_url}'
                    markdown += f'    - [Source code (tar.gz)]({proxy_tar_url})\n'
                else:
                    markdown += f'    - [Source code (tar.gz)]({tar_url})\n'
            
            markdown += '\n'
        
        markdown += '---\n\n'
    
    return markdown

def update_markdown_file(file_path, content):
    """更新Markdown文件内容"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"已更新文件 {file_path}")
        return True
    except Exception as e:
        logger.error(f"更新Markdown文件失败: {str(e)}")
        return False

def update_special_thanks_file():
    """更新特别感谢文件"""
    try:
        # 获取贡献者数据
        contributors_data, success = fetch_github_data(GITHUB_REPO, "contributors", 50)
        if not success or not contributors_data:
            logger.error("无法获取贡献者数据")
            return False
        
        # 格式化为Markdown
        base_content = """# 🙏特别鸣谢\n\n

New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。\n\n

## 👨‍💻 开发贡献者

以下是所有为项目做出贡献的开发者列表。在此感谢他们的辛勤工作和创意！

!!! info "贡献者信息"
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

def update_changelog_file():
    """更新更新日志文件"""
    try:
        # 获取发布数据
        releases_data, success = fetch_github_data(GITHUB_REPO, "releases", 30)
        if not success or not releases_data:
            logger.error("无法获取发布数据")
            return False
        
        # 格式化为Markdown
        releases_markdown = format_releases_markdown(releases_data)
        
        # 更新到文件
        changelog_file = os.path.join(DOCS_DIR, 'docs/wiki/changelog.md')
        return update_markdown_file(changelog_file, releases_markdown)
    
    except Exception as e:
        logger.error(f"更新更新日志失败: {str(e)}")
        return False

def main():
    """主函数 - 智能更新文档"""
    logger.info("启动文档更新服务")
    
    # 初始化变量
    last_update = {
        'contributors': 0,
        'releases': 0
    }
    
    # 设置更新间隔 (单位：秒)
    update_intervals = {
        'contributors': 3600,     # 贡献者列表每小时更新一次
        'releases': 1800          # 发布日志每30分钟更新一次
    }
    
    # 主循环
    while True:
        try:
            current_time = time.time()
            
            # 检查是否需要更新贡献者列表
            if current_time - last_update['contributors'] >= update_intervals['contributors']:
                logger.info("开始更新贡献者列表")
                if update_special_thanks_file():
                    last_update['contributors'] = current_time
                    logger.info("贡献者列表更新成功")
                else:
                    logger.warning("贡献者列表更新失败，将在下次更新周期重试")
            
            # 检查是否需要更新发布日志
            if current_time - last_update['releases'] >= update_intervals['releases']:
                logger.info("开始更新发布日志")
                if update_changelog_file():
                    last_update['releases'] = current_time
                    logger.info("发布日志更新成功")
                else:
                    logger.warning("发布日志更新失败，将在下次更新周期重试")
            
            # 计算下一次检查前的等待时间
            next_check = min(
                last_update['contributors'] + update_intervals['contributors'],
                last_update['releases'] + update_intervals['releases']
            ) - current_time
            
            # 如果时间已经过了，立即再次检查
            if next_check <= 0:
                next_check = 10
            
            # 限制最小和最大等待时间
            next_check = max(min(next_check, 600), 30)
            
            logger.info(f"下次检查将在 {next_check:.0f} 秒后进行")
            time.sleep(next_check)
            
        except Exception as e:
            logger.error(f"更新循环出错: {str(e)}")
            time.sleep(300)  # 出错后等待5分钟再重试

if __name__ == "__main__":
    main()