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
        self.thread_running = False  # 标记线程是否已经在运行
        self.rebuild_triggered = False  # 标记是否已触发重建
        self.rebuild_cooldown = 0  # 重建冷却时间
        self.api_failures = 0  # API失败计数
        self.api_cooldown_until = 0  # API冷却时间
        
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
    """获取GitHub数据"""
    try:
        # 检查API冷却时间
        current_time = time.time()
        if current_time < app_state.api_cooldown_until:
            cooldown_remaining = int(app_state.api_cooldown_until - current_time)
            print(f"[API] GitHub API冷却中，跳过请求 (剩余 {cooldown_remaining} 秒)")
            return None, False
            
        # 构建API URL
        if data_type == "releases":
            api_path = f'repos/{repo}/releases?per_page={count}'
        elif data_type == "contributors":
            api_path = f'repos/{repo}/contributors?per_page={count}'
        else:
            return None, False
            
        # 根据是否使用代理选择适当的API URL
        if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
            # 使用通用代理方式
            original_api_url = f'https://api.github.com/{api_path}'
            # 直接传递原始URL，不进行编码
            api_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={original_api_url}'
        else:
            api_url = f'https://api.github.com/{api_path}'
        
        # 获取GitHub数据
        request = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        try:
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('utf-8'))
            
            # 成功获取数据，重置失败计数
            app_state.api_failures = 0
            
            # 处理分页数据（如果需要）
            if data_type == "contributors" and len(data) < count and len(data) > 0:
                # 如果是贡献者数据，且返回的数量小于请求的数量，尝试获取下一页
                all_data = data.copy()
                page = 2
                
                # 最多获取5页数据，避免过多请求
                while len(all_data) < count and page <= 5:
                    # 构建下一页URL
                    if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                        next_api_url = f'https://api.github.com/{api_path}&page={page}'
                        next_url = f'{GITHUB_PROXY_CONFIG["proxy"]}?url={next_api_url}'
                    else:
                        next_url = f'https://api.github.com/{api_path}&page={page}'
                    
                    next_request = urllib.request.Request(
                        next_url,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    
                    next_response = urllib.request.urlopen(next_request)
                    next_data = json.loads(next_response.read().decode('utf-8'))
                    
                    # 如果没有更多数据，退出循环
                    if not next_data:
                        break
                        
                    all_data.extend(next_data)
                    page += 1
                    
                    # 添加短暂延迟，避免触发GitHub API限制
                    time.sleep(1)
                
                # 限制返回的数据数量
                return all_data[:count], True
            
            return data, True
        except urllib.error.HTTPError as e:
            # 处理HTTP错误
            print(f"获取GitHub数据失败: HTTP Error {e.code}: {e.reason}")
            
            # 如果是限速错误，设置较长的冷却时间
            if e.code == 403 and "rate limit exceeded" in str(e.reason).lower():
                app_state.api_failures += 1
                cooldown_time = 60 * (2 ** min(app_state.api_failures, 6))  # 指数退避，最多64分钟
                app_state.api_cooldown_until = current_time + cooldown_time
                print(f"[API] GitHub API限速，设置冷却时间 {cooldown_time} 秒")
            
            # 如果代理访问失败，尝试直接访问
            if use_proxy and GITHUB_PROXY_CONFIG["enabled"]:
                print("[API] 代理访问失败，尝试直接访问")
                return fetch_github_data(repo, data_type, count, False)
            
            return None, False
        except Exception as e:
            print(f"获取GitHub数据失败: {str(e)}")
            
            # 增加失败计数和冷却时间
            app_state.api_failures += 1
            cooldown_time = 30 * app_state.api_failures  # 线性增加冷却时间
            app_state.api_cooldown_until = current_time + cooldown_time
            print(f"[API] 设置API冷却时间 {cooldown_time} 秒")
            
            return None, False
    except Exception as e:
        print(f"获取GitHub数据失败: {str(e)}")
        return None, False

def check_and_update_cache(repo, data_type, count):
    """检查并更新缓存，如果数据有变化则返回True"""
    cache_file = get_cache_path(repo, data_type, count)
    if not cache_file:
        return False
    
    cache_key = f"{repo}_{data_type}_{count}"
    
    # 如果在过去30分钟内检查过，则跳过
    now = time.time()
    if cache_key in app_state.last_check and now - app_state.last_check[cache_key] < 1800:  # 30分钟
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
        # 如果在冷却期内，跳过触发
        current_time = time.time()
        if current_time < app_state.rebuild_cooldown:
            print(f"[rebuild] 重建冷却中，跳过触发 (剩余 {int(app_state.rebuild_cooldown - current_time)} 秒)")
            return False
            
        # 如果已经触发过重建，跳过
        if app_state.rebuild_triggered:
            print("[rebuild] 已经触发过重建，跳过")
            return False
            
        # 确保有配置文件路径
        if not app_state.config_file or not os.path.exists(app_state.config_file):
            print("[rebuild] 未找到配置文件，无法触发重建")
            return False
        
        # 设置重建标记和冷却时间
        app_state.rebuild_triggered = True
        app_state.rebuild_cooldown = current_time + 60  # 60秒冷却时间
        
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
        
        # 5秒后重置触发标记
        def reset_trigger():
            time.sleep(5)
            app_state.rebuild_triggered = False
            
        threading.Thread(target=reset_trigger, daemon=True).start()
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
    refresh_interval = 300  # 5分钟检查一次
    last_full_refresh = time.time()
    
    print("[auto_refresh] 自动刷新线程已启动")
    
    while app_state.keep_running:
        try:
            current_time = time.time()
            
            # 每12小时执行一次全量刷新
            force_refresh = (current_time - last_full_refresh) >= 43200  # 12小时
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
                            # 添加延迟，避免触发GitHub API限制
                            time.sleep(5)
                        except Exception as e:
                            print(f"[auto_refresh] 创建默认缓存失败: {repo}, {data_type}, {count}, 错误: {str(e)}")
                    
                    # 重新扫描缓存目录
                    cache_files = [f for f in os.listdir(app_state.cache_dir) if f.endswith('.json')]
                    print(f"[auto_refresh] 创建默认缓存后找到 {len(cache_files)} 个缓存文件")
                
                # 限制每次检查的文件数量，避免过多API请求
                max_files_per_check = 2
                files_to_check = cache_files[:max_files_per_check]
                
                for filename in files_to_check:
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
                                
                            # 添加延迟，避免触发GitHub API限制
                            time.sleep(5)
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
        
        # 如果缓存目录为空，创建默认缓存
        cache_files = [f for f in os.listdir(app_state.cache_dir) if f.endswith('.json')]
        if len(cache_files) == 0:
            fetch_and_update_cache("Calcium-Ion/new-api", "releases", 30)
            time.sleep(2)  # 添加短暂延迟
            fetch_and_update_cache("Calcium-Ion/new-api", "contributors", 50)
    except Exception as e:
        print(f"[macros] 初始缓存检查失败: {str(e)}")
    
    # 启动自动刷新线程（如果尚未启动）
    try:
        if not app_state.thread_running:
            print("[macros] 启动自动刷新线程")
            app_state.thread_running = True
            refresh_thread = threading.Thread(target=auto_refresh_worker, daemon=True)
            refresh_thread.start()
            print("[macros] 自动刷新线程已启动")
        else:
            print("[macros] 自动刷新线程已在运行，跳过启动")
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
                    print("[macro] 获取数据失败，返回错误信息")
                    return f'!!! error "数据暂时不可用"\n    GitHub Releases数据暂时不可用，请稍后再试。\n    如果问题持续存在，请联系管理员。\n'
                
                # 保存到缓存
                if cache_file:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(releases, f)
                    print(f"[macro] 已创建缓存: {cache_file}")
            else:
                # 检查缓存是否过期（24小时）
                file_mtime = os.path.getmtime(cache_file)
                cache_age = time.time() - file_mtime
                print(f"[macro] 缓存已存在，缓存年龄: {int(cache_age)}秒")
                
                # 如果缓存过期，在后台触发更新，但仍使用现有缓存
                if cache_age > 86400:  # 24小时
                    print("[macro] 缓存已过期，触发后台更新")
                    # 触发后台异步更新，但不等待结果
                    threading.Thread(
                        target=fetch_and_update_cache, 
                        args=(repo, "releases", count), 
                        daemon=True
                    ).start()
            
            # 从缓存读取数据
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    releases = json.load(f)
                    print(f"[macro] 从缓存加载了 {len(releases)} 个发布")
            except Exception as e:
                print(f"[macro] 读取缓存失败: {str(e)}，返回错误信息")
                return f'!!! error "缓存读取失败"\n    无法读取GitHub Releases缓存数据，请稍后再试。\n    错误详情: {str(e)}\n'
            
            # 获取缓存更新时间
            cache_update_time = datetime.fromtimestamp(os.path.getmtime(cache_file)) if cache_file and os.path.exists(cache_file) else datetime.now()
            
            # 生成Markdown格式
            markdown = ""
            
            # 添加缓存状态信息 - 使用MkDocs原生的Admonition格式
            markdown += f'!!! note "数据信息"\n'
            markdown += f'    数据更新于: {cache_update_time.strftime("%Y-%m-%d %H:%M:%S")} (每30分钟自动检查更新)\n\n'
            
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
                    print("[macro] 获取数据失败，返回错误信息")
                    return f'!!! error "数据暂时不可用"\n    GitHub贡献者数据暂时不可用，请稍后再试。\n    如果问题持续存在，请联系管理员。\n'
                
                # 保存到缓存
                if cache_file:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(contributors, f)
                    print(f"[macro] 已创建缓存: {cache_file}")
            else:
                # 检查缓存是否过期（24小时）
                file_mtime = os.path.getmtime(cache_file)
                cache_age = time.time() - file_mtime
                print(f"[macro] 缓存已存在，缓存年龄: {int(cache_age)}秒")
                
                # 如果缓存过期，在后台触发更新，但仍使用现有缓存
                if cache_age > 86400:  # 24小时
                    print("[macro] 缓存已过期，触发后台更新")
                    # 触发后台异步更新，但不等待结果
                    threading.Thread(
                        target=fetch_and_update_cache, 
                        args=(repo, "contributors", count), 
                        daemon=True
                    ).start()
            
            # 从缓存读取数据
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    contributors = json.load(f)
                    print(f"[macro] 从缓存加载了 {len(contributors)} 个贡献者")
            except Exception as e:
                print(f"[macro] 读取缓存失败: {str(e)}，返回错误信息")
                return f'!!! error "缓存读取失败"\n    无法读取GitHub贡献者缓存数据，请稍后再试。\n    错误详情: {str(e)}\n'
            
            # 获取缓存更新时间
            cache_update_time = datetime.fromtimestamp(os.path.getmtime(cache_file)) if cache_file and os.path.exists(cache_file) else datetime.now()
            
            # 生成Markdown格式的贡献者列表
            markdown = ""
            
            # 添加缓存状态信息 - 使用MkDocs原生的Admonition格式
            markdown += f'!!! note "数据信息"\n'
            markdown += f'    数据更新于: {cache_update_time.strftime("%Y-%m-%d %H:%M:%S")} (每30分钟自动检查更新)\n\n'
            
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