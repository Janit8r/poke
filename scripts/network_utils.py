# -*- coding: utf-8 -*-
"""
网络请求工具模块
提供统一的网络请求、重试机制和错误处理
"""
import time
import random
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import urllib3

from config import NETWORK_CONFIG
from logger_utils import get_logger

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)

class NetworkManager:
    """网络请求管理器"""
    
    def __init__(self):
        self.session = self._create_session()
        self.request_count = 0
        self.success_count = 0
        self.fail_count = 0
    
    def _create_session(self):
        """创建带有重试机制的session"""
        session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=NETWORK_CONFIG['max_retries'],
            backoff_factor=1,
            status_forcelist=NETWORK_CONFIG['retry_status_codes'],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def safe_request(self, url, headers=None, max_retries=None, delay=None, stream=False):
        """
        安全的网络请求，带有重试机制和403处理
        
        Args:
            url: 请求URL
            headers: 请求头
            max_retries: 最大重试次数
            delay: 重试延迟
            stream: 是否流式下载
            
        Returns:
            requests.Response对象或None
        """
        if headers is None:
            headers = NETWORK_CONFIG['headers'].copy()
        
        if max_retries is None:
            max_retries = NETWORK_CONFIG['max_retries']
            
        if delay is None:
            delay = NETWORK_CONFIG['retry_delay']
        
        self.request_count += 1
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"请求: {url} (尝试 {attempt + 1}/{max_retries})")
                
                # 为每次请求添加随机延迟以模拟人类行为
                if attempt > 0:
                    random_delay = random.uniform(1, 3)
                    logger.debug(f"随机延迟: {random_delay:.2f}秒")
                    time.sleep(random_delay)
                
                # 对于403错误，尝试更换User-Agent
                if attempt > 0:
                    headers = self._get_random_headers()
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=NETWORK_CONFIG['timeout'],
                    stream=stream,
                    verify=False,  # 跳过SSL验证
                    allow_redirects=True
                )
                
                # 检查响应状态
                if response.status_code == 403:
                    logger.warning(f"403 Forbidden: {url} - 尝试更换策略")
                    if attempt < max_retries - 1:
                        # 对于403错误，增加更长的延迟
                        extended_delay = delay + random.uniform(5, 10)
                        logger.info(f"403错误，等待 {extended_delay:.1f} 秒后重试...")
                        time.sleep(extended_delay)
                        continue
                    else:
                        raise requests.exceptions.HTTPError(f"403 Client Error: Forbidden for url: {url}")
                
                response.raise_for_status()
                
                self.success_count += 1
                logger.debug(f"请求成功: {url}")
                
                # 添加请求间隔
                if NETWORK_CONFIG['request_delay'] > 0:
                    base_delay = NETWORK_CONFIG['request_delay']
                    actual_delay = base_delay + random.uniform(0.5, 1.5)
                    time.sleep(actual_delay)
                
                return response
                
            except requests.exceptions.RequestException as e:
                error_msg = f"请求失败 (尝试 {attempt + 1}/{max_retries}): {url} - {str(e)}"
                
                if "403" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"{error_msg} - 403错误，将尝试更换策略")
                else:
                    logger.warning(error_msg)
                
                if attempt < max_retries - 1:
                    retry_delay = delay + random.uniform(1, 3)
                    logger.info(f"等待 {retry_delay:.1f} 秒后重试...")
                    time.sleep(retry_delay)
                    delay *= 1.5  # 温和的指数退避
                else:
                    logger.error(f"所有重试都失败了，无法获取: {url}")
                    self.fail_count += 1
                    return None
        
        return None
    
    def _get_random_headers(self):
        """获取随机User-Agent和headers以绕过检测"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        ]
        
        headers = NETWORK_CONFIG['headers'].copy()
        headers['User-Agent'] = random.choice(user_agents)
        
        # 添加Referer
        headers['Referer'] = 'https://wiki.52poke.com/'
        
        return headers
    
    def get_soup(self, url, headers=None):
        """
        获取BeautifulSoup对象
        
        Args:
            url: 请求URL
            headers: 请求头
            
        Returns:
            BeautifulSoup对象或None
        """
        response = self.safe_request(url, headers)
        if response:
            return BeautifulSoup(response.text, "html.parser")
        return None
    
    def download_file(self, url, file_path, headers=None):
        """
        下载文件
        
        Args:
            url: 文件URL
            file_path: 保存路径
            headers: 请求头
            
        Returns:
            bool: 下载是否成功
        """
        try:
            response = self.safe_request(url, headers, stream=True)
            if response:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                logger.debug(f"文件下载成功: {file_path}")
                return True
            else:
                logger.error(f"文件下载失败: {url}")
                return False
        except Exception as e:
            logger.error(f"文件下载异常: {url} - {e}")
            return False
    
    def get_stats(self):
        """获取请求统计信息"""
        return {
            'total_requests': self.request_count,
            'successful_requests': self.success_count,
            'failed_requests': self.fail_count,
            'success_rate': (self.success_count / self.request_count * 100) if self.request_count > 0 else 0
        }

# 全局网络管理器实例
network_manager = NetworkManager()

def safe_request(url, headers=None):
    """便捷的安全请求函数"""
    return network_manager.safe_request(url, headers)

def get_soup(url, headers=None):
    """便捷的获取soup对象函数"""
    return network_manager.get_soup(url, headers)

def download_file(url, file_path, headers=None):
    """便捷的文件下载函数"""
    return network_manager.download_file(url, file_path, headers)

def get_network_stats():
    """获取网络请求统计"""
    return network_manager.get_stats()

