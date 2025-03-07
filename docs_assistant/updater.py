import os
import json
import time
import hashlib
import requests
import logging
from datetime import datetime
import yaml

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
                
                changes_detected = False
                
                # 执行更新
                for repo, data_type, count in update_tasks:
                    cache_changed = update_cache(repo, data_type, count)
                    if cache_changed:
                        changes_detected = True
                    time.sleep(5)  # 避免连续请求
                
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