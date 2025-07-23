"""
日志模块 (Logging Module)

提供统一的日志记录功能，支持多种日志级别和输出格式。
自动管理日志文件轮转和大小控制。

Author: Salieri
Version: 2.0.0
Date: 2025-07
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional
from pathlib import Path

from config import config


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅在控制台输出时使用）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        """格式化日志记录，添加颜色"""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # 临时修改记录的levelname以添加颜色
        original_levelname = record.levelname
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        # 格式化消息
        formatted = super().format(record)
        
        # 恢复原始levelname
        record.levelname = original_levelname
        
        return formatted


class GameAutomationLogger:
    """
    游戏自动化日志记录器
    
    提供统一的日志记录功能，支持同时输出到控制台和文件。
    自动管理日志文件大小和备份。
    
    Attributes:
        logger (logging.Logger): Python标准日志记录器实例
        
    Example:
        >>> logger = get_logger("my_module")
        >>> logger.info("这是一条信息日志")
        >>> logger.warning("这是一条警告日志")
        >>> logger.error("这是一条错误日志")
    """
    
    _instance: Optional['GameAutomationLogger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'GameAutomationLogger':
        """单例模式：确保只有一个日志记录器实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志记录器（只执行一次）"""
        if self._initialized:
            return
            
        self._setup_logging()
        self._initialized = True
    
    def _setup_logging(self) -> None:
        """设置日志记录器配置"""
        # 确保日志目录存在
        log_dir = Path(config.paths.logs_dir)
        log_dir.mkdir(exist_ok=True)
        
        # 获取根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.logging.log_level.upper()))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 创建文件处理器（支持日志轮转）
        log_file = log_dir / "game_automation.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.logging.max_log_size,
            backupCount=config.logging.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, config.logging.log_level.upper()))
        file_formatter = logging.Formatter(
            config.logging.log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 记录初始化信息
        logging.getLogger(__name__).info("日志系统初始化完成")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name (str): 日志记录器名称，通常使用模块名
            
        Returns:
            logging.Logger: 配置好的日志记录器实例
            
        Example:
            >>> log_manager = GameAutomationLogger()
            >>> logger = log_manager.get_logger("vision_utils")
            >>> logger.info("图像检测开始")
        """
        return logging.getLogger(name)


# 全局日志管理器实例
_log_manager = GameAutomationLogger()


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    Args:
        name (str): 日志记录器名称，建议使用 __name__
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
        
    Example:
        >>> from logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("模块初始化完成")
    """
    return _log_manager.get_logger(name)


def log_function_call(func):
    """
    装饰器：自动记录函数调用
    
    Args:
        func: 要装饰的函数
        
    Returns:
        wrapper: 装饰后的函数
        
    Example:
        >>> @log_function_call
        ... def my_function(x, y):
        ...     return x + y
        >>> result = my_function(1, 2)  # 自动记录函数调用
    """
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        logger.debug(f"调用函数 {func.__name__}，参数: args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数 {func.__name__} 执行成功，返回值: {result}")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
    
    return wrapper


def log_execution_time(func):
    """
    装饰器：记录函数执行时间
    
    Args:
        func: 要装饰的函数
        
    Returns:
        wrapper: 装饰后的函数
        
    Example:
        >>> @log_execution_time
        ... def slow_function():
        ...     time.sleep(1)
        >>> slow_function()  # 自动记录执行时间
    """
    import time
    logger = get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.3f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败 (耗时: {execution_time:.3f}秒): {e}")
            raise
    
    return wrapper


class LogContext:
    """
    日志上下文管理器
    
    用于在特定代码块中添加额外的日志信息。
    
    Example:
        >>> with LogContext("图像识别过程"):
        ...     # 在这个代码块中的所有日志都会包含上下文信息
        ...     logger.info("开始检测按钮")
        ...     logger.info("检测完成")
    """
    
    def __init__(self, context_name: str, logger_name: Optional[str] = None):
        """
        初始化日志上下文
        
        Args:
            context_name (str): 上下文名称
            logger_name (str, optional): 日志记录器名称
        """
        self.context_name = context_name
        self.logger = get_logger(logger_name or __name__)
        
    def __enter__(self):
        """进入上下文"""
        self.logger.info(f"🔄 开始 {self.context_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if exc_type is None:
            self.logger.info(f"✅ 完成 {self.context_name}")
        else:
            self.logger.error(f"❌ {self.context_name} 发生错误: {exc_val}")


# 预定义的日志记录器
main_logger = get_logger("main")
vision_logger = get_logger("vision")
state_logger = get_logger("state_machine")
config_logger = get_logger("config")