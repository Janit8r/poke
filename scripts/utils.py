
# -*- coding: utf-8 -*-
"""
通用工具函数模块
提供文件操作、数据处理等通用功能
"""
import base64
import json
import os
from datetime import datetime

from logger_utils import get_logger
from network_utils import download_file

logger = get_logger(__name__)

def save_to_file(file_path, data):
    """
    保存数据到JSON文件
    
    Args:
        file_path: 文件路径
        data: 要保存的数据
    
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding="utf8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
        logger.debug(f"数据保存成功: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"数据保存失败: {file_path} - {e}")
        return False

def load_from_file(file_path):
    """
    从JSON文件加载数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 加载的数据，失败时返回None
    """
    try:
        with open(file_path, 'r', encoding="utf8") as file:
            data = json.load(file)
        
        logger.debug(f"数据加载成功: {file_path}")
        return data
        
    except FileNotFoundError:
        logger.debug(f"文件不存在: {file_path}")
        return None
    except Exception as e:
        logger.error(f"数据加载失败: {file_path} - {e}")
        return None

def file_exists(file_path):
    """
    检查文件是否存在
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 文件是否存在
    """
    return os.path.exists(file_path) and os.path.isfile(file_path)

def get_file_size(file_path):
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节），文件不存在时返回0
    """
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def get_file_mtime(file_path):
    """
    获取文件修改时间
    
    Args:
        file_path: 文件路径
        
    Returns:
        datetime: 文件修改时间，失败时返回None
    """
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except:
        return None

def should_skip_existing_file(file_path, max_age_hours=24):
    """
    判断是否应该跳过现有文件（基于文件年龄）
    
    Args:
        file_path: 文件路径
        max_age_hours: 最大文件年龄（小时），超过此时间的文件将被重新生成
        
    Returns:
        bool: 是否应该跳过现有文件
    """
    if not file_exists(file_path):
        return False
    
    mtime = get_file_mtime(file_path)
    if not mtime:
        return False
    
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    return age_hours <= max_age_hours

def save_image(file_path, url, headers=None):
    """
    保存图片文件（使用统一的网络工具）
    
    Args:
        file_path: 保存路径
        url: 图片URL
        headers: 请求头
        
    Returns:
        bool: 下载是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        success = download_file(url, file_path, headers)
        if success:
            logger.debug(f"图片保存成功: {file_path}")
        else:
            logger.error(f"图片保存失败: {file_path}")
        
        return success
        
    except Exception as e:
        logger.error(f"图片保存异常: {file_path} - {e}")
        return False

def save_base64_image(file_path, data):
    """
    保存base64编码的图片
    
    Args:
        file_path: 保存路径
        data: base64编码的图片数据
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        image_data = base64.b64decode(data)
        with open(file_path, 'wb') as file:
            file.write(image_data)
        
        logger.debug(f"Base64图片保存成功: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Base64图片保存失败: {file_path} - {e}")
        return False

def format_file_size(size_bytes):
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def clean_filename(filename):
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # Windows文件名非法字符
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    # 移除开头和结尾的点和空格
    filename = filename.strip('. ')
    
    # 限制长度
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename

def create_backup_filename(file_path):
    """
    创建备份文件名
    
    Args:
        file_path: 原始文件路径
        
    Returns:
        str: 备份文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(file_path)
    return f"{name}_backup_{timestamp}{ext}"

def get_list_stats(data_list):
    """
    获取列表统计信息
    
    Args:
        data_list: 数据列表
        
    Returns:
        dict: 统计信息
    """
    if not data_list:
        return {"count": 0, "empty": True}
    
    return {
        "count": len(data_list),
        "empty": False,
        "first_item": data_list[0] if data_list else None,
        "last_item": data_list[-1] if data_list else None
    }