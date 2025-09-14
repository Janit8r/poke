# -*- coding: utf-8 -*-
"""
日志记录工具模块
提供统一的日志记录功能
"""
import logging
import logging.handlers
import sys
from datetime import datetime

from config import LOG_CONFIG

# 全局日志器字典
_loggers = {}

def setup_logging():
    """设置日志配置"""
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_CONFIG['level']))
    
    # 清除现有handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter(LOG_CONFIG['format'])
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（轮转日志）
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_CONFIG['log_file'],
            maxBytes=LOG_CONFIG['max_file_size'],
            backupCount=LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create file handler: {e}")

def get_logger(name):
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger对象
    """
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]

class ProgressLogger:
    """进度日志器，用于记录脚本执行进度"""
    
    def __init__(self, script_name):
        self.script_name = script_name
        self.logger = get_logger(f'progress.{script_name}')
        self.start_time = None
        self.current_step = 0
        self.total_steps = 0
        
    def start(self, total_steps=None):
        """开始记录进度"""
        self.start_time = datetime.now()
        self.total_steps = total_steps or 0
        self.current_step = 0
        
        self.logger.info(f"开始执行脚本: {self.script_name}")
        if total_steps:
            self.logger.info(f"预计处理 {total_steps} 个项目")
    
    def update(self, step_name=None, increment=1):
        """更新进度"""
        self.current_step += increment
        
        if step_name:
            self.logger.info(f"[{self.current_step}/{self.total_steps}] {step_name}")
        elif self.total_steps > 0:
            percentage = (self.current_step / self.total_steps) * 100
            self.logger.info(f"进度: {self.current_step}/{self.total_steps} ({percentage:.1f}%)")
    
    def error(self, message, item_name=None):
        """记录错误"""
        if item_name:
            self.logger.error(f"处理失败: {item_name} - {message}")
        else:
            self.logger.error(f"执行错误: {message}")
    
    def warning(self, message, item_name=None):
        """记录警告"""
        if item_name:
            self.logger.warning(f"处理警告: {item_name} - {message}")
        else:
            self.logger.warning(f"执行警告: {message}")
    
    def success(self, message, item_name=None):
        """记录成功"""
        if item_name:
            self.logger.info(f"处理成功: {item_name} - {message}")
        else:
            self.logger.info(f"执行成功: {message}")
    
    def finish(self, success_count=None, fail_count=None):
        """完成进度记录"""
        if self.start_time:
            elapsed_time = datetime.now() - self.start_time
            self.logger.info(f"脚本执行完成: {self.script_name}")
            self.logger.info(f"总耗时: {elapsed_time}")
            
            if success_count is not None and fail_count is not None:
                total = success_count + fail_count
                success_rate = (success_count / total * 100) if total > 0 else 0
                self.logger.info(f"执行结果: 成功 {success_count}, 失败 {fail_count}, 成功率 {success_rate:.1f}%")

class ScriptLogger:
    """脚本专用日志器"""
    
    def __init__(self, script_name):
        self.logger = get_logger(f'script.{script_name}')
        self.script_name = script_name
    
    def info(self, message):
        """记录信息"""
        self.logger.info(f"[{self.script_name}] {message}")
    
    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(f"[{self.script_name}] {message}")
    
    def warning(self, message):
        """记录警告"""
        self.logger.warning(f"[{self.script_name}] {message}")
    
    def error(self, message):
        """记录错误"""
        self.logger.error(f"[{self.script_name}] {message}")
    
    def critical(self, message):
        """记录严重错误"""
        self.logger.critical(f"[{self.script_name}] {message}")

# 初始化日志系统
setup_logging()

