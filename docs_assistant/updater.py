import os
import json
import time
import hashlib
import requests
import logging
from datetime import datetime
import yaml
import re
import threading

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

# 全局状态
class AppState:
    def __init__(self):
        self.api_failures = 0  # API失败计数
        self.api_cooldown_until = 0  # API冷却时间
        self.rebuild_cooldown = 0  # 重建冷却时间
        self.rebuild_triggered = False  # 标记是否已触发重建
        
app_state = AppState()

def fetch_github_data(repo, data_type, count, use_proxy=True):
    """获取GitHub数据"""
    logger.info(f"获取GitHub数据: {repo}, {data_type}, count={count}")
    
    headers = {'User-Agent': 'Mozilla/5.0 DocUpdater/1.0'}
    
    try:
        # 检查API冷却时间
        current_time = time.time()
        if current_time < app_state.api_cooldown_until:
            cooldown_remaining = int(app_state.api_cooldown_until - current_time)
            logger.info(f"GitHub API冷却中，跳过请求 (剩余 {cooldown_remaining} 秒)")
            return None, False
            
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
        response.raise_for_status()
        data = response.json()
        
        # 成功获取数据，重置失败计数
        app_state.api_failures = 0
        
        # 处理分页 (如果需要)
        if data_type == "contributors" and len(data) < count and len(data) > 0:
            all_data = data.copy()
            page = 2
            
            # 最多获取5页
            while len(all_data) < count and page <= 5:
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
                time.sleep(1)  # 避免触发限制
            
            return all_data[:count], True
        
        return data, True
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求失败: {str(e)}")
        
        # 处理限速错误
        if hasattr(e, 'response') and e.response and e.response.status_code == 403 and "rate limit exceeded" in str(e.response.text).lower():
            app_state.api_failures += 1
            cooldown_time = 60 * (2 ** min(app_state.api_failures, 6))  # 指数退避，最多64分钟
            app_state.api_cooldown_until = time.time() + cooldown_time
            logger.warning(f"GitHub API限速，设置冷却时间 {cooldown_time} 秒")
        
        # 如果代理失败，尝试直接访问
        if use_proxy and USE_PROXY:
            logger.info("代理请求失败，尝试直接访问")
            return fetch_github_data(repo, data_type, count, False)
        
        return None, False
    except Exception as e:
        logger.error(f"获取数据时出错: {str(e)}")
        
        # 增加失败计数和冷却时间
        app_state.api_failures += 1
        cooldown_time = 30 * app_state.api_failures  # 线性增加冷却时间
        app_state.api_cooldown_until = time.time() + cooldown_time
        logger.warning(f"设置API冷却时间 {cooldown_time} 秒")
        
        return None, False

def update_mkdocs_timestamp():
    """更新MkDocs配置文件时间戳，触发重建"""
    current_time = time.time()
    if current_time < app_state.rebuild_cooldown:
        logger.info(f"重建冷却中，跳过触发 (剩余 {int(app_state.rebuild_cooldown - current_time)} 秒)")
        return False
        
    if app_state.rebuild_triggered:
        logger.info("已经触发过重建，跳过")
        return False
        
    try:
        # 查找MkDocs配置文件
        config_file = os.path.join(DOCS_DIR, 'mkdocs.yml')
        if os.path.exists(config_file):
            # 设置重建标记和冷却时间
            app_state.rebuild_triggered = True
            app_state.rebuild_cooldown = current_time + 60  # 60秒冷却时间
            
            # 更新时间戳
            os.utime(config_file, None)
            logger.info(f"已更新配置文件 {config_file} 的时间戳")
            
            # 5秒后重置触发标记
            def reset_trigger():
                time.sleep(5)
                app_state.rebuild_triggered = False
                
            threading.Thread(target=reset_trigger, daemon=True).start()
            return True
        else:
            logger.error(f"未找到MkDocs配置文件: {config_file}")
            return False
    except Exception as e:
        logger.error(f"更新时间戳失败: {str(e)}")
        return False

def format_date(date_string):
    """格式化日期"""
    if not date_string:
        return ""
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return date_string

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
    """将贡献者数据格式化为Markdown内容 - 使用原始风格"""
    if not contributors_data or len(contributors_data) == 0:
        return "暂无贡献者数据，请稍后再试。"
    
    # 添加缓存状态信息
    markdown_content = f'''!!! note "数据信息"
    数据更新于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (每30分钟自动检查更新)

'''
    
    # 为每个贡献者创建条目
    for index, contributor in enumerate(contributors_data):
        username = contributor.get('login', '未知用户')
        avatar_url = contributor.get('avatar_url', '')
        profile_url = contributor.get('html_url', '#')
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
        markdown_content += f'### {username}\n\n'
        markdown_content += f'<div class="contributor-simple {medal_class}">\n'
        markdown_content += f'  <div class="avatar-container">\n'
        markdown_content += f'    <img src="{avatar_url}" alt="{username}" class="contributor-avatar" />\n'
        if medal_label:
            markdown_content += f'    {medal_label}\n'
        markdown_content += f'  </div>\n'
        markdown_content += f'  <div class="contributor-details">\n'
        markdown_content += f'    <a href="{profile_url}" target="_blank">{username}</a>\n'
        markdown_content += f'    <span class="contributor-stats">贡献次数: {contributions}</span>\n'
        markdown_content += f'  </div>\n'
        markdown_content += f'</div>\n\n'
        markdown_content += '---\n\n'
    
    # 添加CSS样式
    markdown_content += '''
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
    
    return markdown_content

def format_releases_markdown(releases_data):
    """将发布数据格式化为Markdown内容 - 使用原始风格"""
    if not releases_data or len(releases_data) == 0:
        return "暂无版本数据，请稍后再试。"
    
    markdown_content = "# 📝 更新日志\n\n"
    
    # 添加缓存状态信息
    markdown_content += f'!!! note "数据信息"\n'
    markdown_content += f'    数据更新于: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (每30分钟自动检查更新)\n\n'
    
    # 遍历发布版本
    for index, release in enumerate(releases_data):
        # 获取发布信息
        prerelease = release.get('prerelease', False)
        tag_name = release.get('tag_name', '')
        name = release.get('name') or tag_name
        created_at = format_date(release.get('created_at', ''))
        body = release.get('body', '')
        
        # 处理内容中的图片链接
        if USE_PROXY:
            # 替换Markdown格式的图片链接
            def replace_md_img(match):
                alt_text = match.group(1)
                img_url = match.group(2)
                return f'![{alt_text}]({GITHUB_PROXY}?url={img_url})'
            
            body = re.sub(r'!\[(.*?)\]\((https?://[^)]+)\)', replace_md_img, body)
            
            # 替换HTML格式的图片链接
            def replace_html_img(match):
                prefix = match.group(1)
                img_url = match.group(2)
                suffix = match.group(3)
                return f'<img{prefix}src="{GITHUB_PROXY}?url={img_url}"{suffix}>'
            
            body = re.sub(r'<img([^>]*)src="(https?://[^"]+)"([^>]*)>', replace_html_img, body)
        
        # 处理内容中的标题，确保所有标题至少是三级标题
        # 首先移除原始内容中可能存在的HTML标签
        body = re.sub(r'<[^>]+>', '', body)
        
        # 预处理：统一处理Markdown标题格式
        # 1. 移除每行开头和结尾的空白字符
        body = re.sub(r'^\s+|\s+$', '', body, flags=re.MULTILINE)
        
        # 2. 确保标题前有空行（更好的分隔）
        body = re.sub(r'([^\n])\n(#{1,6} )', r'\1\n\n\2', body)
        
        # 3. 处理标题：依次处理1级到6级标题
        for i in range(1, 7):
            heading = '#' * i
            
            # 改进的标题级别处理:
            # - 一级标题变为三级标题
            # - 其他标题只提升一级，但确保不超过最大级别
            if i == 1:
                new_level = 3  # 一级标题统一变为三级
            else:
                new_level = min(i + 1, 6)  # 其他标题提升一级，但不超过六级
                
            new_heading = '#' * new_level
            
            # 更强大的标题匹配模式，忽略行首空白，确保匹配标题后的空格和内容
            pattern = r'(^|\n)[ \t]*' + re.escape(heading) + r'[ \t]+(.+?)[ \t]*(\n|$)'
            replacement = r'\1' + new_heading + r' \2\3'
            body = re.sub(pattern, replacement, body)
        
        # 版本号作为二级标题
        markdown_content += f'## {tag_name}\n\n'
        
        # 最新版本直接显示"最新版本"，其他版本显示正式/预发布版本
        if index == 0:
            version_type = "最新版本"
        else:
            version_type = "预发布版本" if prerelease else "正式版本"
        
        # 为最新版本使用不同颜色的admonition
        admonition_type = "success" if index == 0 else "info"
        markdown_content += f'???+ {admonition_type} "{version_type} · 发布于 {created_at}"\n\n'
        
        # 缩进内容以适应admonition格式
        indented_body = '\n'.join(['    ' + line for line in body.split('\n')])
        markdown_content += f'{indented_body}\n\n'
        
        # 添加资源下载部分（仍在admonition内部，但作为普通文本）
        assets = release.get('assets', [])
        if assets or tag_name:
            markdown_content += '    **下载资源**\n\n'
            # 添加正常资源
            for asset in assets:
                name = asset.get('name', '')
                url = asset.get('browser_download_url', '')
                # 替换下载URL为代理URL
                if USE_PROXY and 'github.com' in url:
                    url = f'{GITHUB_PROXY}?url={url}'
                size = format_file_size(asset.get('size', 0))
                markdown_content += f'    - [{name}]({url}) ({size})\n'
            
            # 在下载资源部分直接添加源代码下载链接
            if tag_name:
                # 构建zip下载链接
                zip_url = f'https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag_name}.zip'
                if USE_PROXY:
                    proxy_zip_url = f'{GITHUB_PROXY}?url={zip_url}'
                    markdown_content += f'    - [Source code (zip)]({proxy_zip_url})\n'
                else:
                    markdown_content += f'    - [Source code (zip)]({zip_url})\n'
                
                # 构建tar.gz下载链接
                tar_url = f'https://github.com/{GITHUB_REPO}/archive/refs/tags/{tag_name}.tar.gz'
                if USE_PROXY:
                    proxy_tar_url = f'{GITHUB_PROXY}?url={tar_url}'
                    markdown_content += f'    - [Source code (tar.gz)]({proxy_tar_url})\n'
                else:
                    markdown_content += f'    - [Source code (tar.gz)]({tar_url})\n'
            
            markdown_content += '\n'
        
        markdown_content += '---\n\n'
    
    return markdown_content

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
        contributors_markdown = format_contributors_markdown(contributors_data)
        
        # 读取原文件内容
        thanks_file = os.path.join(DOCS_DIR, 'docs/wiki/special-thanks.md')
        if os.path.exists(thanks_file):
            with open(thanks_file, 'r', encoding='utf-8') as f:
                thanks_content = f.read()
            
            # 找到需要替换的部分
            pattern = r'(!!! note "数据信息".*?)(?=\n## |\Z)'
            if re.search(pattern, thanks_content, re.DOTALL):
                # 如果找到了数据信息部分，替换整个部分
                new_content = re.sub(pattern, contributors_markdown, thanks_content, flags=re.DOTALL)
                return update_markdown_file(thanks_file, new_content)
            else:
                # 如果找不到，先查找标题
                title_match = re.search(r'^# (.*?)$', thanks_content, re.MULTILINE)
                if title_match:
                    # 保留标题，添加新内容
                    title = title_match.group(0)
                    new_content = f"{title}\n\n{contributors_markdown}"
                    return update_markdown_file(thanks_file, new_content)
                else:
                    # 如果找不到标题，直接添加内容
                    full_content = f"# New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。\n\n{contributors_markdown}"
                    return update_markdown_file(thanks_file, full_content)
        else:
            # 如果文件不存在，创建包含完整内容的文件
            full_content = f"# New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。\n\n{contributors_markdown}"
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
    """主函数"""
    logger.info("启动文档更新服务")
    
    # 检查MkDocs配置文件
    config_file = os.path.join(DOCS_DIR, 'mkdocs.yml')
    if os.path.exists(config_file):
        logger.info(f"找到MkDocs配置文件: {config_file}")
    else:
        logger.warning(f"未找到MkDocs配置文件: {config_file}")
    
    # 设置初始更新时间
    last_check = 0
    
    # 主循环
    while True:
        try:
            current_time = time.time()
            
            # 检查是否需要更新
            if current_time - last_check >= UPDATE_INTERVAL:
                logger.info("开始检查更新")
                last_check = current_time
                
                # 更新文件
                changes_detected = False
                
                # 更新贡献者列表
                if update_special_thanks_file():
                    changes_detected = True
                    logger.info("已更新贡献者列表")
                
                # 休眠5秒，避免连续请求
                time.sleep(5)
                
                # 更新发布日志
                if update_changelog_file():
                    changes_detected = True
                    logger.info("已更新更新日志")
                
                # 如果有变化，触发MkDocs重建
                if changes_detected:
                    logger.info("检测到变化，触发MkDocs重建")
                    update_mkdocs_timestamp()
                else:
                    logger.info("没有检测到变化，跳过触发重建")
            
            # 休眠一段时间
            sleep_time = 60  # 每分钟检查一次是否需要更新
            logger.debug(f"休眠 {sleep_time} 秒")
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"更新循环出错: {str(e)}")
            time.sleep(300)  # 出错后等待5分钟再重试

if __name__ == "__main__":
    main()