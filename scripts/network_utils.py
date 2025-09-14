# -*- coding: utf-8 -*-
"""
网络请求工具模块
提供统一的网络请求、重试机制和错误处理
"""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from config import NETWORK_CONFIG
from logger_utils import get_logger

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
    
    def safe_request(self, url, headers=None, max_retries=None, delay=None):
        """
        安全的网络请求，带有重试机制和错误处理
        
        Args:
            url: 请求URL
            headers: 请求头
            max_retries: 最大重试次数
            delay: 重试延迟
            
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
                logger.info(f"请求: {url} (尝试 {attempt + 1}/{max_retries})")
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=NETWORK_CONFIG['timeout']
                )
                response.raise_for_status()
                
                self.success_count += 1
                logger.debug(f"请求成功: {url}")
                
                # 添加请求间隔以避免对服务器造成压力
                if NETWORK_CONFIG['request_delay'] > 0:
                    time.sleep(NETWORK_CONFIG['request_delay'])
                
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {url} - {e}")
                
                if attempt < max_retries - 1:
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                    delay *= 2  # 指数退避
                else:
                    logger.error(f"所有重试都失败了，跳过: {url}")
                    self.fail_count += 1
                    return None
        
        return None
    
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
            response = self.safe_request(url, headers)
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

