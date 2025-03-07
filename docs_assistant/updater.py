import os
import json
import time
import hashlib
import requests
import logging
from datetime import datetime
import yaml
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docs-updater')

# 环境变量配置
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 1800))  # 默认30分钟
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'Calcium-Ion/new-api')
CACHE_DIR = os.environ.get('CACHE_DIR', '/app/docs/.cache')
GITHUB_PROXY = os.environ.get('GITHUB_PROXY', 'https://api2.aimage.cc/proxy')
USE_PROXY = os.environ.get('USE_PROXY', 'true').lower() == 'true'
DOCS_DIR = os.environ.get('DOCS_DIR', '/app/docs')

# 确保缓存目录存在
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(repo, data_type, count):
    """获取缓存文件的路径"""
    safe_repo_name = repo.replace("/", "_")
    return os.path.join(CACHE_DIR, f"{safe_repo_name}_{data_type}_{count}.json")

def get_data_hash(data):
    """获取数据的哈希值"""
    if isinstance(data, list):
        hash_data = []
        for item in data[:10]:  # 只使用前10个项目计算哈希
            if isinstance(item, dict):
                if 'tag_name' in item:
                    hash_data.append(f"{item.get('tag_name')}_{item.get('created_at')}")
                elif 'login' in item:
                    hash_data.append(f"{item.get('login')}_{item.get('contributions')}")
        return hashlib.md5(json.dumps(hash_data).encode()).hexdigest()
    return hashlib.md5(json.dumps(data).encode()).hexdigest()

def fetch_github_data(repo, data_type, count, use_proxy=True):
    """获取GitHub数据"""
    logger.info(f"获取GitHub数据: {repo}, {data_type}, count={count}")
    
    headers = {'User-Agent': 'Mozilla/5.0 DocUpdater/1.0'}
    
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
        response.raise_for_status()
        data = response.json()
        
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
        
        # 如果代理失败，尝试直接访问
        if use_proxy and USE_PROXY:
            logger.info("代理请求失败，尝试直接访问")
            return fetch_github_data(repo, data_type, count, False)
        
        return None, False
    except Exception as e:
        logger.error(f"获取数据时出错: {str(e)}")
        return None, False

def update_cache(repo, data_type, count):
    """更新缓存文件"""
    cache_file = get_cache_path(repo, data_type, count)
    cache_changed = False
    
    try:
        # 获取新数据
        new_data, success = fetch_github_data(repo, data_type, count)
        if not success or not new_data:
            logger.error(f"无法获取 {repo} 的 {data_type} 数据")
            return False
        
        # 检查缓存是否存在
        if os.path.exists(cache_file):
            # 加载现有数据
            with open(cache_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            
            # 比较数据是否有变化
            if get_data_hash(old_data) == get_data_hash(new_data):
                logger.info(f"{repo} 的 {data_type} 数据没有变化，跳过更新")
                return False
            else:
                logger.info(f"{repo} 的 {data_type} 数据有变化，更新缓存")
                cache_changed = True
        else:
            logger.info(f"缓存文件不存在，创建 {repo} 的 {data_type} 缓存")
            cache_changed = True
        
        # 更新缓存文件
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(new_data, f)
        
        logger.info(f"已更新 {repo} 的 {data_type} 缓存")
        return cache_changed
    
    except Exception as e:
        logger.error(f"更新缓存失败: {str(e)}")
        return False

def update_mkdocs_timestamp():
    """更新MkDocs配置文件时间戳，触发重建"""
    try:
        # 查找MkDocs配置文件
        config_file = os.path.join(DOCS_DIR, 'mkdocs.yml')
        if os.path.exists(config_file):
            # 更新时间戳
            os.utime(config_file, None)
            logger.info(f"已更新配置文件 {config_file} 的时间戳")
            return True
        else:
            logger.error(f"未找到MkDocs配置文件: {config_file}")
            return False
    except Exception as e:
        logger.error(f"更新时间戳失败: {str(e)}")
        return False

def format_contributors_markdown(contributors_data):
    """将贡献者数据格式化为Markdown内容"""
    if not contributors_data or len(contributors_data) == 0:
        return "暂无贡献者数据，请稍后再试。"
    
    # 生成贡献者卡片的HTML
    cards_html = '<div class="contributor-cards">\n'
    
    for idx, contributor in enumerate(contributors_data):
        login = contributor.get('login', '未知用户')
        avatar_url = contributor.get('avatar_url', '')
        html_url = contributor.get('html_url', '#')
        contributions = contributor.get('contributions', 0)
        
        # 根据排名添加不同的边框样式
        border_class = ""
        if idx == 0:
            border_class = "gold-border"  # 金牌
        elif idx == 1:
            border_class = "silver-border"  # 银牌
        elif idx == 2:
            border_class = "bronze-border"  # 铜牌
        
        cards_html += f'''
<div class="contributor-card {border_class}">
  <div class="contributor-avatar">
    <a href="{html_url}" target="_blank">
      <img src="{avatar_url}" alt="{login}">
    </a>
  </div>
  <div class="contributor-info">
    <div class="contributor-name"><a href="{html_url}" target="_blank">{login}</a></div>
    <div class="contributor-contributions">贡献: {contributions}</div>
  </div>
</div>
'''
    
    cards_html += '</div>\n'
    
    # 添加CSS样式
    css_style = '''
<style>
.contributor-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  margin: 20px 0;
}

.contributor-card {
  width: 130px;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.2s;
}

.contributor-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 10px rgba(0,0,0,0.15);
}

.gold-border {
  border: 2px solid gold;
}

.silver-border {
  border: 2px solid silver;
}

.bronze-border {
  border: 2px solid #cd7f32;
}

.contributor-avatar {
  margin-bottom: 10px;
}

.contributor-avatar img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.contributor-info {
  text-align: center;
}

.contributor-name {
  font-weight: bold;
  margin-bottom: 5px;
}

.contributor-contributions {
  font-size: 0.9em;
  color: #555;
}
</style>
'''
    
    # 生成最终的Markdown内容
    markdown_content = f'''## 👨‍💻 开发贡献者

以下是所有为项目做出贡献的开发者列表。在此感谢他们的辛勤工作和创意！

!!! info "贡献者信息"
    以下贡献者数据从 [GitHub Contributors 页面](https://github.com/{GITHUB_REPO}/graphs/contributors) 自动获取前{len(contributors_data)}名。贡献度前三名分别以金、银、铜牌边框标识。如果您也想为项目做出贡献，欢迎提交 Pull Request。

{css_style}
{cards_html}

> 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
    
    return markdown_content

def format_releases_markdown(releases_data):
    """将发布数据格式化为Markdown内容"""
    if not releases_data or len(releases_data) == 0:
        return "暂无版本数据，请稍后再试。"
    
    markdown_content = "# 📝 更新日志\n\n"
    markdown_content += "!!! warning \"更多版本\"\n"
    markdown_content += f"    如需查看全部历史版本，请访问 [GitHub Releases 页面](https://github.com/{GITHUB_REPO}/releases)，本页面从该页面定时获取最新更新信息。\n\n"
    
    for release in releases_data:
        tag_name = release.get('tag_name', '未知版本')
        name = release.get('name') or tag_name
        published_at = release.get('published_at', '')
        body = release.get('body', '无发布说明')
        
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
        
        markdown_content += f"## {name}\n\n"
        markdown_content += f"发布日期: {formatted_date}\n\n"
        markdown_content += f"{body}\n\n"
        markdown_content += "---\n\n"
    
    markdown_content += f"> 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return markdown_content

def update_markdown_file(file_path, content, tag_pattern=None):
    """更新Markdown文件内容"""
    try:
        original_content = ""
        file_changed = True
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            # 如果提供了标签模式，则只替换标签部分
            if tag_pattern:
                match = re.search(tag_pattern, original_content, re.DOTALL)
                if match:
                    # 只替换标签之间的内容
                    new_content = original_content[:match.start()] + content + original_content[match.end():]
                    
                    # 检查内容是否实际更改
                    if new_content == original_content:
                        logger.info(f"文件 {file_path} 内容未更改，跳过写入")
                        file_changed = False
                    else:
                        # 写入新内容
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        logger.info(f"已更新文件 {file_path} 的标签内容")
                else:
                    # 标签未找到，直接追加内容
                    logger.warning(f"文件 {file_path} 中未找到匹配的标签，将追加内容")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(original_content + "\n\n" + content)
            else:
                # 如果没有标签模式，直接覆盖整个文件
                if original_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"已覆盖更新文件 {file_path}")
                else:
                    logger.info(f"文件 {file_path} 内容未更改，跳过写入")
                    file_changed = False
        else:
            # 文件不存在，创建新文件
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"已创建文件 {file_path}")
        
        return file_changed
    except Exception as e:
        logger.error(f"更新Markdown文件失败: {str(e)}")
        return False

def update_documents_with_github_data():
    """使用缓存的GitHub数据更新文档"""
    changes_detected = False
    
    # 更新发布日志
    releases_cache = get_cache_path(GITHUB_REPO, "releases", 30)
    if os.path.exists(releases_cache):
        try:
            with open(releases_cache, 'r', encoding='utf-8') as f:
                releases_data = json.load(f)
            
            # 格式化为Markdown
            releases_markdown = format_releases_markdown(releases_data)
            
            # 更新到文件
            changelog_file = os.path.join(DOCS_DIR, 'docs/wiki/changelog.md')
            if update_markdown_file(changelog_file, releases_markdown):
                changes_detected = True
                logger.info("已更新更新日志")
            
        except Exception as e:
            logger.error(f"更新更新日志失败: {str(e)}")
    
    # 更新贡献者列表
    contributors_cache = get_cache_path(GITHUB_REPO, "contributors", 50)
    if os.path.exists(contributors_cache):
        try:
            with open(contributors_cache, 'r', encoding='utf-8') as f:
                contributors_data = json.load(f)
            
            # 格式化为Markdown
            contributors_markdown = format_contributors_markdown(contributors_data)
            
            # 更新到文件
            thanks_file = os.path.join(DOCS_DIR, 'docs/wiki/special-thanks.md')
            if os.path.exists(thanks_file):
                # 读取文件内容
                with open(thanks_file, 'r', encoding='utf-8') as f:
                    thanks_content = f.read()
                
                # 找到需要替换的部分
                sections = thanks_content.split("## 👨‍💻 开发贡献者")
                if len(sections) > 1:
                    # 提取第一部分
                    first_part = sections[0].strip()
                    
                    # 拼接新内容
                    new_content = f"{first_part}\n\n{contributors_markdown}"
                    
                    # 更新文件
                    if update_markdown_file(thanks_file, new_content):
                        changes_detected = True
                        logger.info("已更新贡献者列表")
                else:
                    # 如果找不到分隔标记，直接添加内容
                    update_markdown_file(thanks_file, contributors_markdown)
                    changes_detected = True
                    logger.info("已添加贡献者列表")
            else:
                # 如果文件不存在，创建包含完整内容的文件
                full_content = f"# New API 的开发离不开社区的支持和贡献。在此特别感谢所有为项目提供帮助的个人和组织。\n\n{contributors_markdown}"
                update_markdown_file(thanks_file, full_content)
                changes_detected = True
                logger.info("已创建贡献者列表文件")
            
        except Exception as e:
            logger.error(f"更新贡献者列表失败: {str(e)}")
    
    return changes_detected

def main():
    """主函数"""
    logger.info("启动文档更新服务")
    
    # 创建缓存目录
    os.makedirs(CACHE_DIR, exist_ok=True)
    logger.info(f"缓存目录: {CACHE_DIR}")
    
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
                
                # 需要更新的数据
                update_tasks = [
                    (GITHUB_REPO, "releases", 30),
                    (GITHUB_REPO, "contributors", 50)
                ]
                
                cache_changes_detected = False
                
                # 执行更新
                for repo, data_type, count in update_tasks:
                    cache_changed = update_cache(repo, data_type, count)
                    if cache_changed:
                        cache_changes_detected = True
                    time.sleep(5)  # 避免连续请求
                
                # 使用GitHub数据更新文档
                doc_changes_detected = update_documents_with_github_data()
                
                # 如果有变化，触发MkDocs重建
                if cache_changes_detected or doc_changes_detected:
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