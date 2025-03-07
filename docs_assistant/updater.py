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
GITHUB_PROXY = os.environ.get('GITHUB_PROXY', 'https://api2.aimage.cc/proxy')
USE_PROXY = os.environ.get('USE_PROXY', 'true').lower() == 'true'
DOCS_DIR = os.environ.get('DOCS_DIR', '/app/docs')

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
            sections = thanks_content.split("## 👨‍💻 开发贡献者")
            if len(sections) > 1:
                # 提取第一部分
                first_part = sections[0].strip()
                
                # 拼接新内容
                new_content = f"{first_part}\n\n{contributors_markdown}"
                
                # 更新文件
                return update_markdown_file(thanks_file, new_content)
            else:
                # 如果找不到分隔标记，直接添加内容
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