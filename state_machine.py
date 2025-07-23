"""
状态机模块 (State Machine Module)

实现可扩展的状态机系统，用于管理游戏菜单导航和状态转换。
支持动态状态注册、状态转换监控和错误恢复。

Author: Game Automation Team
Version: 2.0.0
Date: 2024-12
"""

import time
from typing import Dict, Callable, Optional, Set, List, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

from config import config
from logger import get_logger, LogContext, log_execution_time
from vision import vision_system, VisionSystem


# 获取模块专用日志记录器
logger = get_logger(__name__)


class StateResult(Enum):
    """状态执行结果枚举"""
    SUCCESS = "success"           # 成功执行并转换到下一状态
    FAILED = "failed"            # 执行失败
    RETRY = "retry"              # 需要重试
    TERMINATED = "terminated"    # 正常终止


@dataclass
class StateTransition:
    """状态转换记录"""
    from_state: str              # 源状态
    to_state: Optional[str]      # 目标状态
    timestamp: float             # 转换时间戳
    execution_time: float        # 执行时间
    result: StateResult          # 执行结果
    error_message: Optional[str] = None  # 错误信息


@dataclass
class StateStats:
    """状态统计信息"""
    execution_count: int = 0     # 执行次数
    success_count: int = 0       # 成功次数
    failure_count: int = 0       # 失败次数
    total_time: float = 0.0      # 总执行时间
    average_time: float = 0.0    # 平均执行时间
    transitions: List[StateTransition] = field(default_factory=list)


class BaseState(ABC):
    """
    状态基类
    
    所有状态都应该继承此类并实现execute方法。
    提供状态生命周期管理和通用功能。
    
    Attributes:
        name (str): 状态名称
        description (str): 状态描述
        vision (VisionSystem): 视觉系统实例
        
    Example:
        >>> class MyState(BaseState):
        ...     def execute(self):
        ...         # 状态逻辑
        ...         return "next_state"
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化状态
        
        Args:
            name (str): 状态名称
            description (str): 状态描述
        """
        self.name = name
        self.description = description or name
        self.vision = vision_system
        self.logger = get_logger(f"state.{name}")
        
        # 状态统计
        self.stats = StateStats()
        
        self.logger.debug(f"状态 {self.name} 初始化完成")
    
    @abstractmethod
    def execute(self) -> Optional[str]:
        """
        执行状态逻辑
        
        Returns:
            str: 下一个状态名称，None表示结束
        """
        pass
    
    def on_enter(self) -> None:
        """状态进入时调用"""
        self.logger.info(f"📘 进入状态: {self.name}")
    
    def on_exit(self, next_state: Optional[str]) -> None:
        """状态退出时调用"""
        self.logger.info(f"📗 退出状态: {self.name} -> {next_state or 'END'}")
    
    def on_error(self, error: Exception) -> Optional[str]:
        """
        错误处理
        
        Args:
            error (Exception): 发生的错误
            
        Returns:
            str: 错误恢复后的状态，None表示无法恢复
        """
        self.logger.error(f"状态 {self.name} 发生错误: {error}")
        return "undefined_menu"  # 默认返回到未定义状态
    
    def can_enter_from(self, from_state: str) -> bool:
        """
        检查是否可以从指定状态进入
        
        Args:
            from_state (str): 源状态名称
            
        Returns:
            bool: 是否允许转换
        """
        return True  # 默认允许所有转换
    
    def get_expected_images(self) -> List[str]:
        """
        获取此状态期望的图像列表
        
        Returns:
            List[str]: 图像文件名列表
        """
        return []
    
    def __str__(self) -> str:
        return f"State({self.name})"
    
    def __repr__(self) -> str:
        return f"State(name='{self.name}', description='{self.description}')"


class ImageBasedState(BaseState):
    """
    基于图像检测的状态
    
    简化了基于图像检测和点击的状态实现。
    自动处理图像等待、点击和状态转换。
    
    Example:
        >>> state = ImageBasedState(
        ...     name="start_menu",
        ...     target_image="btn_solo.png",
        ...     next_state="solo_menu"
        ... )
    """
    
    def __init__(self, name: str, target_image: str, next_state: str,
                 description: str = "", alternative_images: List[str] = None,
                 click_offset: tuple = (0, 0), custom_timeout: int = None):
        """
        初始化基于图像的状态
        
        Args:
            name (str): 状态名称
            target_image (str): 目标图像文件名
            next_state (str): 成功后的下一状态
            description (str): 状态描述
            alternative_images (List[str]): 备选图像列表
            click_offset (tuple): 点击偏移量 (x, y)
            custom_timeout (int): 自定义超时时间
        """
        super().__init__(name, description)
        self.target_image = target_image
        self.next_state = next_state
        self.alternative_images = alternative_images or []
        self.click_offset = click_offset
        self.timeout = custom_timeout or config.vision.timeout
    
    def execute(self) -> Optional[str]:
        """执行基于图像的状态逻辑"""
        images_to_check = [self.target_image] + self.alternative_images
        
        for image in images_to_check:
            if self.vision.find_and_click(image):
                self.logger.info(f"✅ 成功点击图像: {image}")
                time.sleep(config.vision.post_click_delay)
                return self.next_state
        
        self.logger.warning(f"❌ 未找到任何目标图像: {images_to_check}")
        return None
    
    def get_expected_images(self) -> List[str]:
        """返回期望的图像列表"""
        return [self.target_image] + self.alternative_images


class StateMachine:
    """
    状态机主类
    
    管理状态注册、状态转换、错误恢复和统计信息。
    支持动态添加状态和状态转换监控。
    
    Attributes:
        states (Dict[str, BaseState]): 已注册的状态
        current_state (str): 当前状态名称
        
    Example:
        >>> sm = StateMachine()
        >>> sm.register_state(MyState("test_state"))
        >>> sm.run("test_state")
    """
    
    def __init__(self):
        """初始化状态机"""
        self.states: Dict[str, BaseState] = {}
        self.current_state: Optional[str] = None
        self.visited_states: Set[str] = set()
        self.transition_history: List[StateTransition] = []
        
        # 运行控制
        self.is_running: bool = False
        self.stop_count: int = 0
        self.max_stop_count: int = config.state_machine.max_stop_count
        self.break_count: int = config.state_machine.break_count
        
        logger.info("状态机初始化完成")
        
        # 注册默认状态
        self._register_default_states()
    
    def _register_default_states(self) -> None:
        """注册默认状态"""
        # 未定义状态 - 用于错误恢复
        self.register_state(UndefinedMenuState())
        
        # 游戏菜单状态
        self.register_state(ImageBasedState(
            name="start_menu",
            target_image="btn_solo.png",
            next_state="solo_menu",
            description="开始菜单",
            alternative_images=["btn_solo2.png"]
        ))
        
        self.register_state(ImageBasedState(
            name="solo_menu",
            target_image="btn_train.png",
            next_state="train_menu",
            description="单人游戏菜单"
        ))
        
        self.register_state(ImageBasedState(
            name="train_menu",
            target_image="btn_challenge.png",
            next_state="challenge_menu",
            description="训练菜单"
        ))
        
        self.register_state(ImageBasedState(
            name="challenge_menu",
            target_image="btn_play.png",
            next_state="sp_challenge_menu",
            description="挑战菜单"
        ))
        
        self.register_state(ImageBasedState(
            name="sp_challenge_menu",
            target_image="btn_level.png",
            next_state="level_menu",
            description="特殊挑战菜单"
        ))
        
        self.register_state(ImageBasedState(
            name="level_menu",
            target_image="btn_play.png",
            next_state="play_menu",
            description="关卡选择菜单"
        ))
        
        self.register_state(TerminalState("play_menu", "游戏进行中"))
    
    def register_state(self, state: BaseState) -> None:
        """
        注册状态
        
        Args:
            state (BaseState): 要注册的状态实例
            
        Example:
            >>> sm = StateMachine()
            >>> sm.register_state(MyState("custom_state"))
        """
        if state.name in self.states:
            logger.warning(f"状态 {state.name} 已存在，将被覆盖")
        
        self.states[state.name] = state
        logger.info(f"✅ 状态已注册: {state.name}")
    
    def unregister_state(self, state_name: str) -> bool:
        """
        注销状态
        
        Args:
            state_name (str): 要注销的状态名称
            
        Returns:
            bool: 是否成功注销
        """
        if state_name in self.states:
            del self.states[state_name]
            logger.info(f"状态已注销: {state_name}")
            return True
        else:
            logger.warning(f"状态不存在，无法注销: {state_name}")
            return False
    
    def get_state(self, state_name: str) -> Optional[BaseState]:
        """获取状态实例"""
        return self.states.get(state_name)
    
    def list_states(self) -> List[str]:
        """获取所有已注册状态的名称列表"""
        return list(self.states.keys())
    
    @log_execution_time
    def execute_state(self, state_name: str) -> StateTransition:
        """
        执行指定状态
        
        Args:
            state_name (str): 要执行的状态名称
            
        Returns:
            StateTransition: 状态转换记录
        """
        start_time = time.time()
        
        if state_name not in self.states:
            error_msg = f"状态不存在: {state_name}"
            logger.error(error_msg)
            return StateTransition(
                from_state=state_name,
                to_state=None,
                timestamp=start_time,
                execution_time=0.0,
                result=StateResult.FAILED,
                error_message=error_msg
            )
        
        state = self.states[state_name]
        
        with LogContext(f"执行状态 {state_name}"):
            try:
                # 状态进入
                state.on_enter()
                
                # 执行状态逻辑
                next_state = state.execute()
                
                # 更新统计
                execution_time = time.time() - start_time
                state.stats.execution_count += 1
                state.stats.total_time += execution_time
                state.stats.average_time = state.stats.total_time / state.stats.execution_count
                
                if next_state is not None:
                    state.stats.success_count += 1
                    result = StateResult.SUCCESS
                else:
                    state.stats.failure_count += 1
                    result = StateResult.FAILED
                
                # 状态退出
                state.on_exit(next_state)
                
                # 创建转换记录
                transition = StateTransition(
                    from_state=state_name,
                    to_state=next_state,
                    timestamp=start_time,
                    execution_time=execution_time,
                    result=result
                )
                
                # 记录转换
                state.stats.transitions.append(transition)
                self.transition_history.append(transition)
                
                return transition
                
            except Exception as e:
                # 错误处理
                execution_time = time.time() - start_time
                logger.error(f"状态执行异常: {e}")
                
                # 尝试错误恢复
                recovery_state = state.on_error(e)
                
                # 更新统计
                state.stats.execution_count += 1
                state.stats.failure_count += 1
                state.stats.total_time += execution_time
                state.stats.average_time = state.stats.total_time / state.stats.execution_count
                
                # 创建错误转换记录
                transition = StateTransition(
                    from_state=state_name,
                    to_state=recovery_state,
                    timestamp=start_time,
                    execution_time=execution_time,
                    result=StateResult.FAILED,
                    error_message=str(e)
                )
                
                state.stats.transitions.append(transition)
                self.transition_history.append(transition)
                
                return transition
    
    def run(self, initial_state: Optional[str] = None, max_iterations: int = 100) -> bool:
        """
        运行状态机
        
        Args:
            initial_state (str, optional): 初始状态，默认使用配置中的初始状态
            max_iterations (int): 最大迭代次数，防止无限循环
            
        Returns:
            bool: 是否正常结束
            
        Example:
            >>> sm = StateMachine()
            >>> success = sm.run("start_menu")
        """
        self.is_running = True
        self.current_state = initial_state or config.state_machine.initial_state
        self.visited_states.clear()
        self.stop_count = 0
        iteration_count = 0
        
        logger.info(f"🚀 状态机开始运行，初始状态: {self.current_state}")
        
        try:
            while self.is_running and self.current_state and iteration_count < max_iterations:
                iteration_count += 1
                
                # 检查重复状态
                if self.current_state in self.visited_states:
                    self.stop_count += 1
                    logger.warning(f"🔁 检测到重复状态: {self.current_state}, 计数: {self.stop_count}")
                    
                    if self.stop_count >= self.max_stop_count:
                        logger.warning("⛔ 达到最大重复次数，尝试恢复操作")
                        # 尝试按ESC键恢复
                        vision_system.keyboard.press_key(config.state_machine.fallback_key)
                        time.sleep(2)
                        
                    if self.stop_count >= self.break_count:
                        logger.error("⛔ 达到最大中断次数，停止状态机")
                        break
                else:
                    self.stop_count = 0  # 重置计数器
                
                self.visited_states.add(self.current_state)
                
                # 执行当前状态
                transition = self.execute_state(self.current_state)
                
                # 更新当前状态
                self.current_state = transition.to_state
                
                # 状态转换延迟
                if config.state_machine.state_transition_delay > 0:
                    time.sleep(config.state_machine.state_transition_delay)
            
            # 检查结束原因
            if iteration_count >= max_iterations:
                logger.warning(f"⚠️ 达到最大迭代次数 ({max_iterations})，强制停止")
                return False
            elif self.current_state is None:
                logger.info("✅ 状态机正常结束")
                return True
            else:
                logger.info("🛑 状态机被手动停止")
                return True
                
        except KeyboardInterrupt:
            logger.info("⌨️ 用户中断状态机运行")
            return False
        except Exception as e:
            logger.error(f"❌ 状态机运行时发生未处理的异常: {e}")
            return False
        finally:
            self.is_running = False
            logger.info("🏁 状态机运行结束")
    
    def stop(self) -> None:
        """停止状态机运行"""
        self.is_running = False
        logger.info("🛑 状态机停止信号已发送")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取状态机统计信息
        
        Returns:
            Dict: 包含各种统计信息的字典
        """
        total_transitions = len(self.transition_history)
        successful_transitions = sum(1 for t in self.transition_history if t.result == StateResult.SUCCESS)
        
        stats = {
            "total_states": len(self.states),
            "total_transitions": total_transitions,
            "successful_transitions": successful_transitions,
            "success_rate": successful_transitions / total_transitions if total_transitions > 0 else 0,
            "current_state": self.current_state,
            "visited_states": list(self.visited_states),
            "stop_count": self.stop_count,
            "state_details": {}
        }
        
        # 添加各状态的详细统计
        for name, state in self.states.items():
            stats["state_details"][name] = {
                "execution_count": state.stats.execution_count,
                "success_count": state.stats.success_count,
                "failure_count": state.stats.failure_count,
                "average_time": state.stats.average_time,
                "total_time": state.stats.total_time
            }
        
        return stats
    
    def print_statistics(self) -> None:
        """打印状态机统计信息"""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("📊 状态机统计信息")
        print("="*50)
        print(f"总状态数: {stats['total_states']}")
        print(f"总转换次数: {stats['total_transitions']}")
        print(f"成功转换次数: {stats['successful_transitions']}")
        print(f"成功率: {stats['success_rate']:.2%}")
        print(f"当前状态: {stats['current_state']}")
        print(f"重复计数: {stats['stop_count']}")
        
        print("\n📈 各状态统计:")
        for name, details in stats["state_details"].items():
            if details["execution_count"] > 0:
                success_rate = details["success_count"] / details["execution_count"]
                print(f"  {name}: 执行{details['execution_count']}次, "
                      f"成功{details['success_count']}次 ({success_rate:.1%}), "
                      f"平均耗时{details['average_time']:.2f}秒")


class UndefinedMenuState(BaseState):
    """
    未定义菜单状态
    
    用于错误恢复和状态识别。
    尝试识别当前界面并返回到已知状态。
    """
    
    def __init__(self):
        super().__init__("undefined_menu", "未定义菜单状态 - 用于错误恢复")
    
    def execute(self) -> Optional[str]:
        """尝试识别当前界面"""
        # 移动鼠标到安全位置
        self.vision.mouse.move_to(10, 10)
        
        # 检测可能的界面
        detection_map = {
            "btn_solo.png": "start_menu",
            "btn_train.png": "solo_menu", 
            "train_menu.png": "train_menu"
        }
        
        for image, state_name in detection_map.items():
            if self.vision.is_image_present(image):
                self.logger.info(f"🔍 检测到 {image} → 转到 {state_name}")
                return state_name
        
        # 如果无法识别，按ESC键并保持在当前状态
        self.logger.warning("❌ 无法判断当前界面，按 ESC 键尝试恢复")
        self.vision.keyboard.press_key(config.state_machine.fallback_key)
        time.sleep(1)
        
        return "undefined_menu"


class TerminalState(BaseState):
    """
    终端状态
    
    表示状态机的结束状态，不会转换到其他状态。
    """
    
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
    
    def execute(self) -> Optional[str]:
        """终端状态，返回None结束状态机"""
        self.logger.info(f"🏁 到达终端状态: {self.name}")
        return None


# 全局状态机实例
state_machine = StateMachine()


# 装饰器：用于注册状态处理函数（兼容原代码）
def state(name: str):
    """
    状态注册装饰器（兼容性）
    
    Args:
        name (str): 状态名称
        
    Example:
        >>> @state("my_state")
        ... def handle_my_state():
        ...     return "next_state"
    """
    def decorator(func):
        # 将函数包装为状态类
        class FunctionState(BaseState):
            def __init__(self):
                super().__init__(name, f"Function-based state: {name}")
                self.handler_func = func
            
            def execute(self) -> Optional[str]:
                return self.handler_func()
        
        # 注册状态
        state_machine.register_state(FunctionState())
        return func
    
    return decorator