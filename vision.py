"""
计算机视觉模块 (Computer Vision Module)

提供游戏UI元素检测、图像匹配、鼠标键盘控制等功能。
支持多种图像匹配算法和错误恢复机制。

Author: Game Automation Team
Version: 2.0.0
Date: 2024-12
"""

import cv2
import numpy as np
import pyautogui
import time
import mss
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from pynput.keyboard import Controller, Key

from config import config
from logger import get_logger, log_execution_time, LogContext


# 获取模块专用日志记录器
logger = get_logger(__name__)

# 键盘控制器实例
keyboard = Controller()


@dataclass
class MatchResult:
    """图像匹配结果"""
    found: bool                    # 是否找到匹配
    position: Optional[Tuple[int, int]]  # 匹配位置 (x, y)
    confidence: float              # 匹配置信度 (0.0-1.0)
    template_size: Tuple[int, int] # 模板图像大小 (width, height)
    match_time: float              # 匹配耗时 (秒)


@dataclass
class ClickResult:
    """点击操作结果"""
    success: bool                  # 是否成功点击
    position: Tuple[int, int]      # 点击位置 (x, y)
    click_time: float              # 点击耗时 (秒)
    error_message: Optional[str]   # 错误信息


class ImageMatcher:
    """
    图像匹配器
    
    负责在屏幕上查找指定的UI元素图像。
    支持多种匹配算法和参数配置。
    
    Attributes:
        threshold (float): 图像匹配阈值
        timeout (int): 匹配超时时间
        check_interval (float): 检查间隔
        
    Example:
        >>> matcher = ImageMatcher()
        >>> result = matcher.find_image("btn_solo.png")
        >>> if result.found:
        ...     print(f"找到按钮，位置: {result.position}")
    """
    
    def __init__(self, threshold: Optional[float] = None, 
                 timeout: Optional[int] = None,
                 check_interval: Optional[float] = None):
        """
        初始化图像匹配器
        
        Args:
            threshold (float, optional): 匹配阈值，默认使用配置值
            timeout (int, optional): 超时时间，默认使用配置值
            check_interval (float, optional): 检查间隔，默认使用配置值
        """
        self.threshold = threshold or config.vision.threshold
        self.timeout = timeout or config.vision.timeout
        self.check_interval = check_interval or config.vision.check_interval
        
        logger.info(f"图像匹配器初始化完成 - 阈值: {self.threshold}, 超时: {self.timeout}s")
    
    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """
        加载模板图像
        
        Args:
            template_path (str): 模板图像路径
            
        Returns:
            np.ndarray: 加载的灰度图像，加载失败返回None
        """
        try:
            full_path = config.get_image_path(template_path)
            template = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
            
            if template is None:
                logger.error(f"无法加载图像文件: {full_path}")
                return None
                
            logger.debug(f"成功加载模板图像: {template_path}, 尺寸: {template.shape}")
            return template
            
        except Exception as e:
            logger.error(f"加载模板图像时发生异常: {e}")
            return None
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """
        捕获屏幕截图
        
        Returns:
            np.ndarray: 屏幕截图的灰度图像，失败返回None
        """
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # 主显示器
                screenshot = np.array(sct.grab(monitor))
                # 转换为灰度图像 (BGR -> Gray)
                gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
                return gray_screen
                
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return None
    
    @log_execution_time
    def find_image(self, template_path: str, 
                   region: Optional[Tuple[int, int, int, int]] = None) -> MatchResult:
        """
        在屏幕上查找指定图像
        
        Args:
            template_path (str): 模板图像文件名
            region (tuple, optional): 搜索区域 (x, y, width, height)
            
        Returns:
            MatchResult: 匹配结果
            
        Example:
            >>> matcher = ImageMatcher()
            >>> result = matcher.find_image("btn_solo.png")
            >>> if result.found:
            ...     print(f"匹配置信度: {result.confidence}")
        """
        start_time = time.time()
        
        with LogContext(f"查找图像 {template_path}"):
            # 加载模板图像
            template = self._load_template(template_path)
            if template is None:
                return MatchResult(
                    found=False, position=None, confidence=0.0,
                    template_size=(0, 0), match_time=time.time() - start_time
                )
            
            h, w = template.shape
            template_size = (w, h)
            
            # 在指定时间内循环查找
            while time.time() - start_time < self.timeout:
                # 捕获屏幕
                screen = self._capture_screen()
                if screen is None:
                    time.sleep(self.check_interval)
                    continue
                
                # 如果指定了搜索区域，则裁剪屏幕
                if region:
                    x, y, rw, rh = region
                    screen = screen[y:y+rh, x:x+rw]
                    offset_x, offset_y = x, y
                else:
                    offset_x, offset_y = 0, 0
                
                # 模板匹配
                try:
                    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= self.threshold:
                        # 计算中心位置
                        center_x = max_loc[0] + w // 2 + offset_x
                        center_y = max_loc[1] + h // 2 + offset_y
                        
                        match_time = time.time() - start_time
                        logger.info(f"图像匹配成功: {template_path}, 位置: ({center_x}, {center_y}), "
                                  f"置信度: {max_val:.3f}, 耗时: {match_time:.3f}s")
                        
                        return MatchResult(
                            found=True,
                            position=(center_x, center_y),
                            confidence=max_val,
                            template_size=template_size,
                            match_time=match_time
                        )
                
                except Exception as e:
                    logger.error(f"模板匹配过程中发生错误: {e}")
                
                time.sleep(self.check_interval)
            
            # 超时未找到
            match_time = time.time() - start_time
            logger.warning(f"图像匹配超时: {template_path}, 耗时: {match_time:.3f}s")
            
            return MatchResult(
                found=False, position=None, confidence=0.0,
                template_size=template_size, match_time=match_time
            )
    
    def wait_for_image(self, template_path: str, 
                       custom_timeout: Optional[int] = None) -> Optional[Tuple[int, int]]:
        """
        等待图像出现（兼容性方法）
        
        Args:
            template_path (str): 模板图像文件名
            custom_timeout (int, optional): 自定义超时时间
            
        Returns:
            Tuple[int, int]: 图像中心位置，未找到返回None
        """
        original_timeout = self.timeout
        if custom_timeout:
            self.timeout = custom_timeout
            
        try:
            result = self.find_image(template_path)
            return result.position if result.found else None
        finally:
            self.timeout = original_timeout


class MouseController:
    """
    鼠标控制器
    
    提供精确的鼠标移动和点击功能。
    支持点击验证和错误恢复。
    
    Example:
        >>> mouse = MouseController()
        >>> result = mouse.click(100, 200)
        >>> if result.success:
        ...     print("点击成功")
    """
    
    def __init__(self):
        """初始化鼠标控制器"""
        self.click_duration = config.vision.click_duration
        self.post_click_delay = config.vision.post_click_delay
        logger.info("鼠标控制器初始化完成")
    
    @log_execution_time
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> bool:
        """
        移动鼠标到指定位置
        
        Args:
            x (int): 目标X坐标
            y (int): 目标Y坐标
            duration (float, optional): 移动持续时间
            
        Returns:
            bool: 是否成功移动
        """
        duration = duration or self.click_duration
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.debug(f"鼠标移动到位置: ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"鼠标移动失败: {e}")
            return False
    
    @log_execution_time
    def click(self, x: int, y: int, button: str = 'left',
              duration: Optional[float] = None,
              post_delay: Optional[float] = None) -> ClickResult:
        """
        在指定位置点击鼠标
        
        Args:
            x (int): 点击X坐标
            y (int): 点击Y坐标
            button (str): 鼠标按钮 ('left', 'right', 'middle')
            duration (float, optional): 移动持续时间
            post_delay (float, optional): 点击后延迟时间
            
        Returns:
            ClickResult: 点击操作结果
        """
        start_time = time.time()
        duration = duration or self.click_duration
        post_delay = post_delay or self.post_click_delay
        
        try:
            # 移动到目标位置
            if not self.move_to(x, y, duration):
                return ClickResult(
                    success=False,
                    position=(x, y),
                    click_time=time.time() - start_time,
                    error_message="鼠标移动失败"
                )
            
            # 执行点击
            pyautogui.click(button=button)
            
            # 等待延迟
            if post_delay > 0:
                time.sleep(post_delay)
            
            click_time = time.time() - start_time
            logger.info(f"🖱️ 鼠标点击成功: ({x}, {y}), 按钮: {button}, 耗时: {click_time:.3f}s")
            
            return ClickResult(
                success=True,
                position=(x, y),
                click_time=click_time,
                error_message=None
            )
            
        except Exception as e:
            click_time = time.time() - start_time
            error_msg = f"点击操作失败: {e}"
            logger.error(error_msg)
            
            return ClickResult(
                success=False,
                position=(x, y),
                click_time=click_time,
                error_message=error_msg
            )
    
    def double_click(self, x: int, y: int) -> ClickResult:
        """双击指定位置"""
        try:
            self.move_to(x, y)
            pyautogui.doubleClick()
            time.sleep(self.post_click_delay)
            
            logger.info(f"🖱️ 双击成功: ({x}, {y})")
            return ClickResult(True, (x, y), 0.0, None)
        except Exception as e:
            error_msg = f"双击失败: {e}"
            logger.error(error_msg)
            return ClickResult(False, (x, y), 0.0, error_msg)


class KeyboardController:
    """
    键盘控制器
    
    提供键盘按键和组合键功能。
    
    Example:
        >>> kb = KeyboardController()
        >>> kb.press_key(Key.esc)
        >>> kb.type_text("hello world")
    """
    
    def __init__(self):
        """初始化键盘控制器"""
        self.keyboard = Controller()
        logger.info("键盘控制器初始化完成")
    
    def press_key(self, key, duration: float = 0.1) -> bool:
        """
        按下并释放按键
        
        Args:
            key: 按键 (可以是Key枚举值或字符串)
            duration (float): 按键持续时间
            
        Returns:
            bool: 是否成功按键
        """
        try:
            self.keyboard.press(key)
            time.sleep(duration)
            self.keyboard.release(key)
            
            logger.debug(f"⌨️ 按键成功: {key}")
            return True
        except Exception as e:
            logger.error(f"按键失败: {e}")
            return False
    
    def key_combination(self, *keys) -> bool:
        """
        按下组合键
        
        Args:
            *keys: 按键序列
            
        Returns:
            bool: 是否成功
            
        Example:
            >>> kb.key_combination(Key.ctrl, 'c')  # Ctrl+C
        """
        try:
            # 按下所有键
            for key in keys:
                self.keyboard.press(key)
            
            time.sleep(0.1)
            
            # 释放所有键（逆序）
            for key in reversed(keys):
                self.keyboard.release(key)
            
            logger.debug(f"⌨️ 组合键成功: {'+'.join(str(k) for k in keys)}")
            return True
        except Exception as e:
            logger.error(f"组合键失败: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        输入文本
        
        Args:
            text (str): 要输入的文本
            interval (float): 字符间隔时间
            
        Returns:
            bool: 是否成功
        """
        try:
            for char in text:
                self.keyboard.type(char)
                time.sleep(interval)
            
            logger.debug(f"⌨️ 文本输入成功: {text}")
            return True
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
            return False


class VisionSystem:
    """
    视觉系统主类
    
    整合图像匹配、鼠标控制、键盘控制等功能。
    提供高级的UI交互方法。
    
    Example:
        >>> vision = VisionSystem()
        >>> success = vision.find_and_click("btn_solo.png")
        >>> if success:
        ...     print("按钮点击成功")
    """
    
    def __init__(self):
        """初始化视觉系统"""
        self.matcher = ImageMatcher()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        
        logger.info("视觉系统初始化完成")
    
    def find_and_click(self, template_path: str, 
                       retries: Optional[int] = None,
                       click_offset: Tuple[int, int] = (0, 0)) -> bool:
        """
        查找图像并点击
        
        Args:
            template_path (str): 模板图像文件名
            retries (int, optional): 重试次数
            click_offset (tuple): 点击偏移量 (x_offset, y_offset)
            
        Returns:
            bool: 是否成功找到并点击
            
        Example:
            >>> vision = VisionSystem()
            >>> success = vision.find_and_click("btn_solo.png", retries=3)
        """
        retries = retries or config.vision.retries
        
        with LogContext(f"查找并点击 {template_path}"):
            for attempt in range(retries):
                logger.info(f"第 {attempt + 1}/{retries} 次尝试")
                
                # 查找图像
                result = self.matcher.find_image(template_path)
                
                if result.found:
                    # 计算点击位置（添加偏移）
                    click_x = result.position[0] + click_offset[0]
                    click_y = result.position[1] + click_offset[1]
                    
                    # 执行点击
                    click_result = self.mouse.click(click_x, click_y)
                    
                    if click_result.success:
                        logger.info(f"✅ 成功找到并点击: {template_path}")
                        return True
                    else:
                        logger.warning(f"点击失败: {click_result.error_message}")
                else:
                    logger.warning(f"未找到图像: {template_path}")
                
                # 失败后的恢复操作
                if attempt < retries - 1:
                    logger.info(f"尝试按 ESC 键恢复...")
                    self.keyboard.press_key(Key.esc)
                    time.sleep(config.vision.delay_between_retries)
            
            logger.error(f"❌ 达到最大重试次数，仍未成功: {template_path}")
            return False
    
    def wait_for_any_image(self, template_paths: List[str], 
                          timeout: Optional[int] = None) -> Optional[str]:
        """
        等待任意一个图像出现
        
        Args:
            template_paths (List[str]): 模板图像文件名列表
            timeout (int, optional): 超时时间
            
        Returns:
            str: 首先出现的图像文件名，超时返回None
        """
        timeout = timeout or config.vision.timeout
        start_time = time.time()
        
        logger.info(f"等待任意图像出现: {template_paths}")
        
        while time.time() - start_time < timeout:
            for template_path in template_paths:
                result = self.matcher.find_image(template_path)
                if result.found:
                    logger.info(f"✅ 检测到图像: {template_path}")
                    return template_path
            
            time.sleep(config.vision.check_interval)
        
        logger.warning(f"⏰ 等待超时，未检测到任何图像")
        return None
    
    def is_image_present(self, template_path: str) -> bool:
        """
        检查图像是否存在（快速检查）
        
        Args:
            template_path (str): 模板图像文件名
            
        Returns:
            bool: 图像是否存在
        """
        # 使用较短的超时时间进行快速检查
        original_timeout = self.matcher.timeout
        self.matcher.timeout = 1  # 1秒快速检查
        
        try:
            result = self.matcher.find_image(template_path)
            return result.found
        finally:
            self.matcher.timeout = original_timeout


# 全局视觉系统实例
vision_system = VisionSystem()

# 为了兼容性，保留原有的函数接口
def wait_for_image(template_path: str, threshold: float = 0.8, 
                   timeout: int = 30, check_interval: float = 0.5) -> Optional[Tuple[int, int]]:
    """兼容性函数：等待图像出现"""
    matcher = ImageMatcher(threshold=threshold, timeout=timeout, check_interval=check_interval)
    return matcher.wait_for_image(template_path)

def robust_wait_image(template_path: str, threshold: float = 0.8, timeout: int = 30,
                     check_interval: float = 0.5, retries: int = 3, 
                     fallback_key=Key.esc, delay_between_retries: float = 2.0) -> Optional[Tuple[int, int]]:
    """兼容性函数：鲁棒的图像等待"""
    return vision_system.find_and_click(template_path) and vision_system.matcher.find_image(template_path).position

def move_and_click(x: int, y: int) -> None:
    """兼容性函数：移动并点击"""
    vision_system.mouse.click(x, y)

def press_key(key) -> None:
    """兼容性函数：按键"""
    vision_system.keyboard.press_key(key)