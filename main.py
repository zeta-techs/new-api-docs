import json
import re
import urllib.request
from datetime import datetime
import os

def define_env(env):
    """
    这个钩子函数用于定义要在模板中使用的变量和宏
    """
    
    @env.macro
    def get_github_releases(repo="Calcium-Ion/new-api", count=10):
        """
        获取GitHub Releases数据并转换为Markdown
        """
        try:
            # 创建缓存目录（如果不存在）
            cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, f'{repo.replace("/", "_")}_releases.json')
            
            # 检查缓存是否存在且不超过1小时
            use_cache = False
            if os.path.exists(cache_file):
                file_mtime = os.path.getmtime(cache_file)
                if (datetime.now().timestamp() - file_mtime) < 3600:  # 1小时缓存
                    use_cache = True
            
            if use_cache:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    releases = json.load(f)
            else:
                # 获取GitHub Releases数据
                request = urllib.request.Request(
                    f'https://api.github.com/repos/{repo}/releases?per_page={count}',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response = urllib.request.urlopen(request)
                releases = json.loads(response.read().decode('utf-8'))
                
                # 保存到缓存
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(releases, f)
            
            # 生成原生Markdown格式
            markdown = ""
            
            # 遍历发布版本
            for index, release in enumerate(releases):
                # 获取发布信息
                prerelease = release.get('prerelease', False)
                tag_name = release.get('tag_name', '')
                created_at = format_date(release.get('created_at', ''))
                body = release.get('body', '')
                
                # 修复Markdown格式的图片链接
                body = re.sub(r'!\[(.*?)\]\((.*?)\)', r'![\1](\2)', body)
                
                # 将HTML格式的图片转换为Markdown格式
                body = re.sub(r'<img([^>]*)src="([^"]*)"([^>]*)>', r'![](\2)', body)
                
                # 处理内容中的标题，将标题级别递增
                # 依次处理6级到1级标题，避免重复替换
                for i in range(6, 0, -1):
                    heading = '#' * i
                    new_heading = '#' * (i + 1)
                    body = re.sub(f'^{heading} (.+?)$', f'{new_heading} \\1', body, flags=re.MULTILINE)
                
                # 版本号作为二级标题
                markdown += f'## {tag_name}\n\n'
                
                # 最新版本直接显示"最新版本"，其他版本显示正式/预发布版本
                if index == 0:
                    version_type = "最新版本"
                else:
                    version_type = "预发布版本" if prerelease else "正式版本"
                
                # 为最新版本使用不同颜色的admonition
                admonition_type = "success" if index == 0 else "info"
                markdown += f'???+ {admonition_type} "{version_type} · 发布于 {created_at}"\n\n'
                
                # 缩进内容以适应admonition格式
                indented_body = '\n'.join(['    ' + line for line in body.split('\n')])
                markdown += f'{indented_body}\n\n'
                
                # 添加资源下载部分（仍在admonition内部，但作为普通文本）
                assets = release.get('assets', [])
                if assets:
                    markdown += '    **下载资源**\n\n'
                    for asset in assets:
                        name = asset.get('name', '')
                        url = asset.get('browser_download_url', '')
                        size = format_file_size(asset.get('size', 0))
                        markdown += f'    - [{name}]({url}) ({size})\n'
                    markdown += '\n'
                
                markdown += '---\n\n'
            
            return markdown
        except Exception as e:
            return f'!!! error "错误"\n    获取GitHub Releases失败: {str(e)}\n'
    
    @env.macro
    def get_github_contributors(repo="Calcium-Ion/new-api", count=100):
        """
        获取GitHub贡献者数据并转换为Markdown
        """
        try:
            # 创建缓存目录（如果不存在）
            cache_dir = os.path.join(os.path.dirname(__file__), '.cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, f'{repo.replace("/", "_")}_contributors.json')
            
            # 检查缓存是否存在且不超过1小时
            use_cache = False
            if os.path.exists(cache_file):
                file_mtime = os.path.getmtime(cache_file)
                if (datetime.now().timestamp() - file_mtime) < 3600:  # 1小时缓存
                    use_cache = True
            
            if use_cache:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    contributors = json.load(f)
            else:
                # 获取GitHub贡献者数据
                request = urllib.request.Request(
                    f'https://api.github.com/repos/{repo}/contributors?per_page={count}',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response = urllib.request.urlopen(request)
                contributors = json.loads(response.read().decode('utf-8'))
                
                # 保存到缓存
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(contributors, f)
            
            # 生成Markdown格式的贡献者列表
            markdown = ""
            
            # 为每个贡献者创建三级标题和简单信息
            for index, contributor in enumerate(contributors):
                username = contributor.get('login', '')
                avatar_url = contributor.get('avatar_url', '')
                profile_url = contributor.get('html_url', '')
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
        except Exception as e:
            return f'!!! error "错误"\n    获取GitHub贡献者失败: {str(e)}\n'
    
    def format_date(date_string):
        """格式化日期"""
        if not date_string:
            return ""
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except:
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