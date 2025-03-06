import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
import os
import time
import threading
import hashlib

# 自定义GitHub代理设置
GITHUB_PROXY_CONFIG = {
    "proxy": "https://api2.aimage.cc/proxy",  # 通用代理
    "enabled": False
}

# 存储全局状态
class AppState:
    def __init__(self):
        self.cache_dir = None
        self.config_file = None
        self.keep_running = True
        self.last_check = {}  # 存储最后一次检查的时间
        
app_state = AppState()

def get_cache_path(repo, data_type, count):
    """获取缓存文件的路径"""
    if not app_state.cache_dir:
        return None
        
    safe_repo_name = repo.replace("/", "_")
    return os.path.join(app_state.cache_dir, f"{safe_repo_name}_{data_type}_{count}.json")

def get_data_hash(data):
    """获取数据的哈希值以便比较差异"""
    if isinstance(data, list):
        # 对于列表，我们关注前10个元素的ID或主要标识符
        hash_data = []
        for item in data[:10]:
            if isinstance(item, dict):
                # 对于发布版本，使用tag_name和created_at
                if 'tag_name' in item:
                    hash_data.append(f"{item.get('tag_name')}_{item.get('created_at')}")
                # 对于贡献者，使用login和contributions
                elif 'login' in item:
                    hash_data.append(f"{item.get('login')}_{item.get('contributions')}")
        return hashlib.md5(json.dumps(hash_data).encode()).hexdigest()
    return hashlib.md5(json.dumps(data).encode()).hexdigest()

def fetch_github_data(repo, data_type, count, use_proxy=True):
    """获取GitHub数据，返回数据和是否成功的标志"""
    try:
        # 根据数据类型确定API端点
        if data_type == "releases":
            # 根据是否使用代理选择适当的API URL
            if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                original_api_url = f'https://api.github.com/repos/{repo}/releases?per_page={count}'
                api_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={original_api_url}'
            else:
                api_url = f'https://api.github.com/repos/{repo}/releases?per_page={count}'
            
            # 获取GitHub Releases数据
            request = urllib.request.Request(
                api_url,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            response = urllib.request.urlopen(request)
            return json.loads(response.read().decode('utf-8')), True
            
        elif data_type == "contributors":
            # 初始化贡献者列表
            contributors = []
            page = 1
            per_page = 100  # GitHub API 每页最多返回100个结果
            
            # 循环获取所有页面的贡献者，直到达到请求的数量
            while len(contributors) < count:
                # 根据是否使用代理选择适当的API URL
                if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                    original_api_url = f'https://api.github.com/repos/{repo}/contributors?per_page={per_page}&page={page}'
                    api_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={original_api_url}'
                else:
                    api_url = f'https://api.github.com/repos/{repo}/contributors?per_page={per_page}&page={page}'
                
                # 获取GitHub贡献者数据
                request = urllib.request.Request(
                    api_url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                response = urllib.request.urlopen(request)
                page_contributors = json.loads(response.read().decode('utf-8'))
                
                # 如果返回的结果为空，说明已经没有更多贡献者了
                if not page_contributors:
                    break
                
                # 添加到总列表
                contributors.extend(page_contributors)
                
                # 增加页码
                page += 1
            
            # 限制贡献者数量为请求的数量
            contributors = contributors[:count]
            return contributors, True
            
        return None, False
    except Exception as e:
        print(f"获取GitHub数据失败: {str(e)}")
        # 如果代理访问失败，尝试直接访问
        if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
            return fetch_github_data(repo, data_type, count, False)
        return None, False

def check_and_update_cache(repo, data_type, count):
    """检查并更新缓存，如果数据有变化则返回True"""
    cache_file = get_cache_path(repo, data_type, count)
    if not cache_file:
        return False
    
    cache_key = f"{repo}_{data_type}_{count}"
    
    # 如果在过去5分钟内检查过，则跳过
    now = time.time()
    if cache_key in app_state.last_check and now - app_state.last_check[cache_key] < 300:
        return False
    
    app_state.last_check[cache_key] = now
    
    try:
        # 获取新数据
        new_data, success = fetch_github_data(repo, data_type, count)
        if not success or not new_data:
            return False
        
        # 检查缓存文件是否存在
        if os.path.exists(cache_file):
            # 加载现有数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 比较数据是否有变化
            if get_data_hash(old_data) == get_data_hash(new_data):
                # 数据相同，无需更新
                return False
        
        # 更新缓存文件
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f)
        
        print(f"[cache] 已更新 {repo} 的 {data_type} 数据")
        
        # 触发MkDocs重新构建
        trigger_mkdocs_rebuild()
        
        return True
    except Exception as e:
        print(f"检查缓存更新失败: {str(e)}")
        return False

def trigger_mkdocs_rebuild():
    """触发MkDocs重新构建"""
    try:
        # 确保有配置文件路径
        if not app_state.config_file or not os.path.exists(app_state.config_file):
            print("[rebuild] 未找到配置文件，无法触发重建")
            return False
        
        # 方法一：通过修改 mkdocs.yml 时间戳触发重建
        print(f"[rebuild] 正在触发MkDocs重建...")
        os.utime(app_state.config_file, None)
        
        # 方法二：寻找一个docs目录下的文件并更新它（如果方法一失效可用）
        docs_dir = os.path.join(os.path.dirname(app_state.config_file), 'docs')
        if os.path.exists(docs_dir):
            # 找到第一个markdown文件并更新时间戳
            for root, _, files in os.walk(docs_dir):
                for file in files:
                    if file.endswith('.md'):
                        trigger_file = os.path.join(root, file)
                        os.utime(trigger_file, None)
                        print(f"[rebuild] 已更新文件 {trigger_file} 的时间戳")
                        break
                if 'trigger_file' in locals():
                    break
        
        print("[rebuild] MkDocs重建已触发")
        return True
    except Exception as e:
        print(f"[rebuild] 触发MkDocs重建失败: {str(e)}")
        return False

def fetch_and_update_cache(repo, data_type, count):
    """强制从GitHub获取数据并更新缓存"""
    cache_file = get_cache_path(repo, data_type, count)
    if not cache_file:
        return False
    
    try:
        # 获取新数据
        new_data, success = fetch_github_data(repo, data_type, count)
        if not success or not new_data:
            return False
        
        # 更新缓存文件
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f)
        
        print(f"[cache] 已强制更新 {repo} 的 {data_type} 数据")
        
        # 触发MkDocs重新构建
        trigger_mkdocs_rebuild()
        
        return True
    except Exception as e:
        print(f"强制更新缓存失败: {str(e)}")
        return False

def auto_refresh_worker():
    """自动刷新工作线程"""
    refresh_interval = 300  # 10秒检查一次 (开发期间用10秒，正式使用可改回300秒)
    last_full_refresh = time.time()
    
    print("[auto_refresh] 自动刷新线程已启动")
    
    while app_state.keep_running:
        try:
            current_time = time.time()
            
            # 每小时执行一次全量刷新
            force_refresh = (current_time - last_full_refresh) >= 3600
            if force_refresh:
                last_full_refresh = current_time
                print("[auto_refresh] 执行全量缓存刷新")
            
            # 扫描缓存目录中的所有文件
            if app_state.cache_dir and os.path.exists(app_state.cache_dir):
                print(f"[auto_refresh] 开始扫描缓存目录: {app_state.cache_dir}")
                cache_files = [f for f in os.listdir(app_state.cache_dir) if f.endswith('.json')]
                print(f"[auto_refresh] 找到 {len(cache_files)} 个缓存文件")
                
                # 如果没有找到任何缓存文件，创建默认缓存
                if len(cache_files) == 0:
                    print("[auto_refresh] 缓存目录为空，创建默认缓存文件")
                    # 创建常用的默认缓存
                    default_caches = [
                        ("Calcium-Ion/new-api", "releases", 30),
                        ("Calcium-Ion/new-api", "contributors", 50)
                    ]
                    
                    for repo, data_type, count in default_caches:
                        try:
                            print(f"[auto_refresh] 创建默认缓存: {repo}, {data_type}, {count}")
                            fetch_and_update_cache(repo, data_type, count)
                        except Exception as e:
                            print(f"[auto_refresh] 创建默认缓存失败: {repo}, {data_type}, {count}, 错误: {str(e)}")
                    
                    # 重新扫描缓存目录
                    cache_files = [f for f in os.listdir(app_state.cache_dir) if f.endswith('.json')]
                    print(f"[auto_refresh] 创建默认缓存后找到 {len(cache_files)} 个缓存文件")
                
                for filename in cache_files:
                    try:
                        # 从文件名解析信息
                        parts = filename.replace('.json', '').split('_')
                        if len(parts) >= 3:
                            repo = parts[0] + '/' + parts[1]
                            data_type = parts[2]
                            count = int(parts[3]) if len(parts) > 3 else 30
                            
                            print(f"[auto_refresh] 处理缓存: {repo}, {data_type}, {count}")
                            
                            # 检查并更新缓存，全量刷新时忽略时间检查
                            if force_refresh:
                                # 强制更新缓存
                                fetch_and_update_cache(repo, data_type, count)
                            else:
                                # 正常检查缓存
                                check_and_update_cache(repo, data_type, count)
                    except Exception as e:
                        print(f"[auto_refresh] 处理缓存文件 {filename} 时出错: {str(e)}")
            else:
                print(f"[auto_refresh] 缓存目录不存在或无法访问: {app_state.cache_dir}")
                
                # 尝试创建缓存目录
                try:
                    os.makedirs(app_state.cache_dir, exist_ok=True)
                    print(f"[auto_refresh] 已创建缓存目录: {app_state.cache_dir}")
                except Exception as e:
                    print(f"[auto_refresh] 创建缓存目录失败: {str(e)}")
            
            # 休眠指定的间隔时间
            print(f"[auto_refresh] 检查完成，等待 {refresh_interval} 秒后再次检查")
            time.sleep(refresh_interval)
        except Exception as e:
            print(f"[auto_refresh] 自动刷新线程出错: {str(e)}")
            time.sleep(60)  # 出错后等待1分钟再重试

def define_env(env):
    """
    这个钩子函数用于定义要在模板中使用的变量和宏
    """
    # 初始化缓存目录和配置文件路径
    config_dir = os.path.dirname(env.conf['config_file_path'])
    app_state.cache_dir = os.path.join(config_dir, '.cache')
    app_state.config_file = env.conf['config_file_path']
    
    # 创建缓存目录
    os.makedirs(app_state.cache_dir, exist_ok=True)
    
    print(f"[macros] 初始化缓存目录: {app_state.cache_dir}")
    
    # 立即执行一次缓存检查
    try:
        # 检查常用的缓存
        print("[macros] 执行初始缓存检查")
        fetch_and_update_cache("Calcium-Ion/new-api", "releases", 30)
        fetch_and_update_cache("Calcium-Ion/new-api", "contributors", 50)
    except Exception as e:
        print(f"[macros] 初始缓存检查失败: {str(e)}")
    
    # 启动自动刷新线程
    try:
        print("[macros] 启动自动刷新线程")
        refresh_thread = threading.Thread(target=auto_refresh_worker, daemon=True)
        refresh_thread.start()
        print("[macros] 自动刷新线程已启动")
    except Exception as e:
        print(f"[macros] 启动自动刷新线程失败: {str(e)}")
    
    # 注册关闭函数
    def cleanup():
        print("[macros] 正在关闭自动刷新线程")
        app_state.keep_running = False
    
    env.conf['plugins']['macros'].on_shutdown = cleanup
    
    @env.macro
    def get_github_releases(repo="Calcium-Ion/new-api", count=30, use_proxy=True):
        """
        获取GitHub Releases数据并转换为Markdown
        """
        try:
            print(f"[macro] 正在获取 GitHub Releases: {repo}, count={count}")
            
            # 缓存文件路径
            cache_file = get_cache_path(repo, "releases", count)
            
            # 检查缓存文件是否存在
            if not cache_file or not os.path.exists(cache_file):
                print("[macro] 缓存不存在，获取新数据")
                # 如果缓存不存在，立即获取新数据
                releases, success = fetch_github_data(repo, "releases", count, use_proxy)
                if not success or not releases:
                    print("[macro] 获取数据失败")
                    return f'!!! error "错误"\n    获取GitHub Releases失败，请稍后再试\n'
                
                # 保存到缓存
                if cache_file:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(releases, f)
                    print(f"[macro] 已创建缓存: {cache_file}")
            else:
                # 检查缓存是否过期（1小时）
                file_mtime = os.path.getmtime(cache_file)
                cache_age = time.time() - file_mtime
                print(f"[macro] 缓存已存在，缓存年龄: {cache_age:.0f}秒")
                
                if cache_age > 3600:  # 1小时缓存
                    print("[macro] 缓存已过期，触发后台更新")
                    # 触发后台异步更新，但不等待结果
                    threading.Thread(
                        target=fetch_and_update_cache, 
                        args=(repo, "releases", count), 
                        daemon=True
                    ).start()
            
            # 从缓存读取数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                releases = json.load(f)
                print(f"[macro] 从缓存加载了 {len(releases)} 个发布")
            
            # 获取缓存更新时间
            cache_update_time = datetime.fromtimestamp(os.path.getmtime(cache_file)) if cache_file and os.path.exists(cache_file) else datetime.now()
            
            # 生成Markdown格式
            markdown = ""
            
            # 添加缓存状态信息 - 使用MkDocs原生的Admonition格式
            markdown += f'!!! note "数据信息"\n'
            markdown += f'    数据更新于: {cache_update_time.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            
            # 遍历发布版本
            for index, release in enumerate(releases):
                # 获取发布信息
                prerelease = release.get('prerelease', False)
                tag_name = release.get('tag_name', '')
                created_at = format_date(release.get('created_at', ''))
                body = release.get('body', '')
                
                # 处理内容中的图片链接
                if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                    # 替换Markdown格式的图片链接
                    def replace_md_img(match):
                        alt_text = match.group(1)
                        img_url = match.group(2)
                        return f'![{alt_text}]({GITHUB_PROXY_CONFIG["proxy"]}?url={img_url})'
                    
                    body = re.sub(r'!\[(.*?)\]\((https?://[^)]+)\)', replace_md_img, body)
                    
                    # 替换HTML格式的图片链接
                    def replace_html_img(match):
                        prefix = match.group(1)
                        img_url = match.group(2)
                        suffix = match.group(3)
                        return f'<img{prefix}src="{GITHUB_PROXY_CONFIG["proxy"]}?url={img_url}"{suffix}>'
                    
                    body = re.sub(r'<img([^>]*)src="(https?://[^"]+)"([^>]*)>', replace_html_img, body)
                else:
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
                if assets or tag_name:
                    markdown += '    **下载资源**\n\n'
                    # 添加正常资源
                    for asset in assets:
                        name = asset.get('name', '')
                        url = asset.get('browser_download_url', '')
                        # 替换下载URL为代理URL
                        if use_proxy and GITHUB_PROXY_CONFIG["enabled"] and 'github.com' in url:
                            # 直接传递原始URL，不进行编码
                            url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={url}'
                        size = format_file_size(asset.get('size', 0))
                        markdown += f'    - [{name}]({url}) ({size})\n'
                    
                    # 在下载资源部分直接添加源代码下载链接
                    if tag_name:
                        # 构建zip下载链接
                        zip_url = f'https://github.com/{repo}/archive/refs/tags/{tag_name}.zip'
                        if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                            proxy_zip_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={zip_url}'
                            markdown += f'    - [Source code (zip)]({proxy_zip_url})\n'
                        else:
                            markdown += f'    - [Source code (zip)]({zip_url})\n'
                        
                        # 构建tar.gz下载链接
                        tar_url = f'https://github.com/{repo}/archive/refs/tags/{tag_name}.tar.gz'
                        if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                            proxy_tar_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={tar_url}'
                            markdown += f'    - [Source code (tar.gz)]({proxy_tar_url})\n'
                        else:
                            markdown += f'    - [Source code (tar.gz)]({tar_url})\n'
                    
                    markdown += '\n'
                
                markdown += '---\n\n'
            
            return markdown
        except Exception as e:
            return f'!!! error "错误"\n    获取GitHub Releases失败: {str(e)}\n'
    
    @env.macro
    def get_github_contributors(repo="Calcium-Ion/new-api", count=50, use_proxy=True):
        """
        获取GitHub贡献者数据并转换为Markdown
        """
        try:
            print(f"[macro] 正在获取 GitHub Contributors: {repo}, count={count}")
            
            # 缓存文件路径
            cache_file = get_cache_path(repo, "contributors", count)
            
            # 检查缓存文件是否存在
            if not cache_file or not os.path.exists(cache_file):
                print("[macro] 缓存不存在，获取新数据")
                # 如果缓存不存在，立即获取新数据
                contributors, success = fetch_github_data(repo, "contributors", count, use_proxy)
                if not success or not contributors:
                    print("[macro] 获取数据失败")
                    return f'!!! error "错误"\n    获取GitHub贡献者失败，请稍后再试\n'
                
                # 保存到缓存
                if cache_file:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(contributors, f)
                    print(f"[macro] 已创建缓存: {cache_file}")
            else:
                # 检查缓存是否过期（1小时）
                file_mtime = os.path.getmtime(cache_file)
                cache_age = time.time() - file_mtime
                print(f"[macro] 缓存已存在，缓存年龄: {cache_age:.0f}秒")
                
                if cache_age > 3600:  # 1小时缓存
                    print("[macro] 缓存已过期，触发后台更新")
                    # 触发后台异步更新，但不等待结果
                    threading.Thread(
                        target=fetch_and_update_cache, 
                        args=(repo, "contributors", count), 
                        daemon=True
                    ).start()
            
            # 从缓存读取数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                contributors = json.load(f)
                print(f"[macro] 从缓存加载了 {len(contributors)} 个贡献者")
            
            # 获取缓存更新时间
            cache_update_time = datetime.fromtimestamp(os.path.getmtime(cache_file)) if cache_file and os.path.exists(cache_file) else datetime.now()
            
            # 生成Markdown格式的贡献者列表
            markdown = ""
            
            # 添加缓存状态信息 - 使用MkDocs原生的Admonition格式
            markdown += f'!!! note "数据信息"\n'
            markdown += f'    数据更新于: {cache_update_time.strftime("%Y-%m-%d %H:%M:%S")}\n\n'
            
            # 为每个贡献者创建三级标题和简单信息
            for index, contributor in enumerate(contributors):
                username = contributor.get('login', '')
                avatar_url = contributor.get('avatar_url', '')
                # 替换头像URL为代理URL - 使用通用代理方式
                if use_proxy and GITHUB_PROXY_CONFIG["enabled"] and 'githubusercontent.com' in avatar_url:
                    # 直接传递原始URL，不进行编码
                    avatar_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={avatar_url}'
                profile_url = contributor.get('html_url', '')
                # 替换个人主页URL为代理URL
                if use_proxy and GITHUB_PROXY_CONFIG["enabled"] and 'github.com' in profile_url:
                    # 直接传递原始URL，不进行编码
                    profile_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={profile_url}'
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
            print(f"[macro] 生成贡献者列表失败: {str(e)}")
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