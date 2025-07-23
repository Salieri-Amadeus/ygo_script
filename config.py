"""
配置模块 (Configuration Module)

此模块包含游戏自动化脚本的所有配置参数和设置。
通过集中管理配置，可以轻松调整脚本行为而无需修改核心代码。

Author: Salieri
Version: 2.0.0
Date: 2025-07
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class VisionConfig:
    """计算机视觉相关配置"""
    threshold: float = 0.8                 # 图像匹配阈值 (0.0-1.0)
    timeout: int = 5                       # 图像等待超时时间 (秒)
    check_interval: float = 0.5            # 检查间隔 (秒)
    retries: int = 3                       # 重试次数
    delay_between_retries: float = 2.0     # 重试间隔 (秒)
    click_duration: float = 0.2            # 鼠标移动持续时间 (秒)
    post_click_delay: float = 1.0          # 点击后等待时间 (秒)


@dataclass
class StateMachineConfig:
    """状态机相关配置"""
    initial_state: str = "undefined_menu"  # 初始状态
    max_stop_count: int = 5                # 最大重复次数
    break_count: int = 8                   # 最大中断次数
    fallback_key: str = "esc"             # 失败时按键
    state_transition_delay: float = 0.1    # 状态转换延迟 (秒)


@dataclass
class PathConfig:
    """路径相关配置"""
    images_dir: str = "images"             # 图像文件夹路径
    logs_dir: str = "logs"                 # 日志文件夹路径
    config_file: str = "config.json"       # 配置文件路径


@dataclass
class LogConfig:
    """日志相关配置"""
    log_level: str = "INFO"                # 日志级别
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_log_size: int = 10 * 1024 * 1024   # 最大日志文件大小 (10MB)
    backup_count: int = 5                  # 日志备份数量


class Config:
    """
    主配置类
    
    管理所有配置参数，支持从JSON文件加载和保存配置。
    提供配置验证和默认值管理功能。
    
    Attributes:
        vision (VisionConfig): 计算机视觉配置
        state_machine (StateMachineConfig): 状态机配置
        paths (PathConfig): 路径配置
        logging (LogConfig): 日志配置
    
    Example:
        >>> config = Config()
        >>> config.load_from_file("config.json")
        >>> print(config.vision.threshold)
        0.8
    """
    
    def __init__(self):
        """初始化配置，使用默认值"""
        self.vision = VisionConfig()
        self.state_machine = StateMachineConfig()
        self.paths = PathConfig()
        self.logging = LogConfig()
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        Path(self.paths.images_dir).mkdir(exist_ok=True)
        Path(self.paths.logs_dir).mkdir(exist_ok=True)
    
    def load_from_file(self, config_path: Optional[str] = None) -> bool:
        """
        从JSON文件加载配置
        
        Args:
            config_path (str, optional): 配置文件路径。默认使用paths.config_file
            
        Returns:
            bool: 是否成功加载配置
            
        Example:
            >>> config = Config()
            >>> success = config.load_from_file("my_config.json")
            >>> if success:
            ...     print("配置加载成功")
        """
        if config_path is None:
            config_path = self.paths.config_file
            
        try:
            if not os.path.exists(config_path):
                print(f"⚠️ 配置文件 {config_path} 不存在，使用默认配置")
                return False
                
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 更新配置
            if 'vision' in data:
                self._update_dataclass(self.vision, data['vision'])
            if 'state_machine' in data:
                self._update_dataclass(self.state_machine, data['state_machine'])
            if 'paths' in data:
                self._update_dataclass(self.paths, data['paths'])
            if 'logging' in data:
                self._update_dataclass(self.logging, data['logging'])
                
            print(f"✅ 成功从 {config_path} 加载配置")
            self._ensure_directories()
            return True
            
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return False
    
    def save_to_file(self, config_path: Optional[str] = None) -> bool:
        """
        保存配置到JSON文件
        
        Args:
            config_path (str, optional): 配置文件路径。默认使用paths.config_file
            
        Returns:
            bool: 是否成功保存配置
            
        Example:
            >>> config = Config()
            >>> config.vision.threshold = 0.9
            >>> config.save_to_file()
        """
        if config_path is None:
            config_path = self.paths.config_file
            
        try:
            data = {
                'vision': asdict(self.vision),
                'state_machine': asdict(self.state_machine),
                'paths': asdict(self.paths),
                'logging': asdict(self.logging)
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"✅ 配置已保存到 {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")
            return False
    
    def _update_dataclass(self, target, source: Dict[str, Any]) -> None:
        """更新数据类实例的属性"""
        for key, value in source.items():
            if hasattr(target, key):
                setattr(target, key, value)
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            bool: 配置是否有效
        """
        errors = []
        
        # 验证视觉配置
        if not 0 <= self.vision.threshold <= 1:
            errors.append("vision.threshold 必须在 0-1 之间")
        if self.vision.timeout <= 0:
            errors.append("vision.timeout 必须大于 0")
        if self.vision.check_interval <= 0:
            errors.append("vision.check_interval 必须大于 0")
        if self.vision.retries < 1:
            errors.append("vision.retries 必须大于等于 1")
            
        # 验证状态机配置
        if self.state_machine.max_stop_count < 1:
            errors.append("state_machine.max_stop_count 必须大于等于 1")
        if self.state_machine.break_count < 1:
            errors.append("state_machine.break_count 必须大于等于 1")
            
        # 验证路径配置
        if not self.paths.images_dir:
            errors.append("paths.images_dir 不能为空")
            
        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
            
        print("✅ 配置验证通过")
        return True
    
    def get_image_path(self, image_name: str) -> str:
        """
        获取图像文件的完整路径
        
        Args:
            image_name (str): 图像文件名
            
        Returns:
            str: 图像文件的完整路径
            
        Example:
            >>> config = Config()
            >>> path = config.get_image_path("btn_solo.png")
            >>> print(path)
            images/btn_solo.png
        """
        return os.path.join(self.paths.images_dir, image_name)
    
    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return (
            f"Config(\n"
            f"  vision={self.vision},\n"
            f"  state_machine={self.state_machine},\n"
            f"  paths={self.paths},\n"
            f"  logging={self.logging}\n"
            f")"
        )


# 全局配置实例
config = Config()

# 自动加载配置文件（如果存在）
config.load_from_file()