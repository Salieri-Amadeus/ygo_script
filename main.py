"""
游戏自动化主程序 (Game Automation Main Program)

这是游戏自动化系统的入口程序。
整合了配置管理、日志系统、计算机视觉和状态机模块。

Author: Game Automation Team
Version: 2.0.0
Date: 2024-12

Usage:
    python main.py                    # 使用默认配置运行
    python main.py --config custom.json  # 使用自定义配置文件
    python main.py --stats            # 运行完成后显示统计信息
    python main.py --help             # 显示帮助信息
"""

import sys
import argparse
import signal
import time
from typing import Optional

# 导入自定义模块
from config import config
from logger import get_logger, LogContext
from state_machine import state_machine, StateMachine
from vision import vision_system


# 获取主程序日志记录器
logger = get_logger(__name__)


class GameAutomationApp:
    """
    游戏自动化应用主类
    
    管理整个应用的生命周期，包括初始化、运行和清理。
    提供命令行接口和信号处理功能。
    
    Attributes:
        state_machine (StateMachine): 状态机实例
        running (bool): 应用运行状态
        
    Example:
        >>> app = GameAutomationApp()
        >>> app.run()
    """
    
    def __init__(self):
        """初始化应用"""
        self.state_machine = state_machine
        self.running = False
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 游戏自动化应用初始化完成")
    
    def _signal_handler(self, signum, frame):
        """处理系统信号（如Ctrl+C）"""
        logger.info(f"📡 接收到信号 {signum}，准备安全退出...")
        self.stop()
    
    def _validate_environment(self) -> bool:
        """
        验证运行环境
        
        Returns:
            bool: 环境是否满足运行要求
        """
        logger.info("🔍 验证运行环境...")
        
        # 验证配置
        if not config.validate():
            logger.error("❌ 配置验证失败")
            return False
        
        # 检查图像文件
        missing_images = []
        for state_name, state_obj in self.state_machine.states.items():
            expected_images = state_obj.get_expected_images()
            for image in expected_images:
                image_path = config.get_image_path(image)
                import os
                if not os.path.exists(image_path):
                    missing_images.append(image)
        
        if missing_images:
            logger.warning(f"⚠️ 发现缺失的图像文件: {missing_images}")
            logger.warning("这可能导致某些状态无法正常工作")
        
        # 测试视觉系统
        try:
            test_result = vision_system.matcher._capture_screen()
            if test_result is None:
                logger.error("❌ 屏幕截图功能测试失败")
                return False
            logger.info("✅ 屏幕截图功能正常")
        except Exception as e:
            logger.error(f"❌ 视觉系统测试失败: {e}")
            return False
        
        logger.info("✅ 环境验证通过")
        return True
    
    def _display_system_info(self) -> None:
        """显示系统信息"""
        logger.info("="*60)
        logger.info("🎮 游戏自动化系统信息")
        logger.info("="*60)
        logger.info(f"版本: 2.0.0")
        logger.info(f"配置文件: {config.paths.config_file}")
        logger.info(f"图像目录: {config.paths.images_dir}")
        logger.info(f"日志目录: {config.paths.logs_dir}")
        logger.info(f"初始状态: {config.state_machine.initial_state}")
        logger.info(f"已注册状态数: {len(self.state_machine.states)}")
        logger.info(f"已注册状态: {', '.join(self.state_machine.list_states())}")
        logger.info("="*60)
    
    def run(self, initial_state: Optional[str] = None, 
            show_stats: bool = False, max_iterations: int = 100) -> bool:
        """
        运行游戏自动化系统
        
        Args:
            initial_state (str, optional): 初始状态
            show_stats (bool): 是否显示统计信息
            max_iterations (int): 最大迭代次数
            
        Returns:
            bool: 是否成功运行
        """
        self.running = True
        
        try:
            with LogContext("游戏自动化系统运行"):
                # 显示系统信息
                self._display_system_info()
                
                # 验证环境
                if not self._validate_environment():
                    logger.error("❌ 环境验证失败，无法启动")
                    return False
                
                logger.info("🎯 准备启动状态机...")
                
                # 运行状态机
                success = self.state_machine.run(
                    initial_state=initial_state,
                    max_iterations=max_iterations
                )
                
                if success:
                    logger.info("🏆 游戏自动化系统运行完成")
                else:
                    logger.warning("⚠️ 游戏自动化系统运行中断")
                
                # 显示统计信息
                if show_stats:
                    self.state_machine.print_statistics()
                
                return success
                
        except Exception as e:
            logger.error(f"💥 系统运行时发生未处理的异常: {e}")
            return False
        finally:
            self.running = False
            logger.info("🏁 游戏自动化系统已停止")
    
    def stop(self) -> None:
        """停止应用"""
        if self.running:
            logger.info("🛑 正在停止游戏自动化系统...")
            self.state_machine.stop()
            self.running = False
        else:
            logger.info("ℹ️ 系统已经停止")
    
    def interactive_mode(self) -> None:
        """
        交互模式
        
        允许用户通过命令行交互控制系统。
        """
        logger.info("🎮 进入交互模式")
        logger.info("可用命令:")
        logger.info("  start [state]  - 启动状态机（可选指定初始状态）")
        logger.info("  stop           - 停止状态机")
        logger.info("  status         - 显示当前状态")
        logger.info("  stats          - 显示统计信息")
        logger.info("  states         - 列出所有状态")
        logger.info("  config         - 显示配置信息")
        logger.info("  help           - 显示帮助")
        logger.info("  quit           - 退出程序")
        
        while True:
            try:
                command = input("\n🎮 > ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                
                if cmd == "start":
                    initial_state = parts[1] if len(parts) > 1 else None
                    if not self.running:
                        logger.info(f"启动状态机，初始状态: {initial_state or '默认'}")
                        self.run(initial_state=initial_state, show_stats=True)
                    else:
                        logger.warning("状态机已在运行中")
                
                elif cmd == "stop":
                    if self.running:
                        self.stop()
                    else:
                        logger.info("状态机未运行")
                
                elif cmd == "status":
                    logger.info(f"当前状态: {self.state_machine.current_state}")
                    logger.info(f"运行状态: {'运行中' if self.running else '已停止'}")
                
                elif cmd == "stats":
                    self.state_machine.print_statistics()
                
                elif cmd == "states":
                    states = self.state_machine.list_states()
                    logger.info(f"已注册状态 ({len(states)}): {', '.join(states)}")
                
                elif cmd == "config":
                    logger.info(f"配置信息:\n{config}")
                
                elif cmd == "help":
                    logger.info("命令帮助已显示在上方")
                
                elif cmd in ["quit", "exit", "q"]:
                    logger.info("👋 退出交互模式")
                    break
                
                else:
                    logger.warning(f"未知命令: {command}")
                    
            except KeyboardInterrupt:
                logger.info("\n👋 用户中断，退出交互模式")
                break
            except Exception as e:
                logger.error(f"命令执行错误: {e}")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        description="游戏自动化系统 - 基于计算机视觉的游戏菜单导航",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                        # 使用默认配置运行
  python main.py --config custom.json   # 使用自定义配置文件
  python main.py --state start_menu     # 从指定状态开始
  python main.py --stats                # 运行完成后显示统计信息
  python main.py --interactive          # 进入交互模式
  python main.py --max-iterations 50    # 设置最大迭代次数
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="配置文件路径 (默认: config.json)"
    )
    
    parser.add_argument(
        "--state", "-s",
        type=str,
        help="初始状态名称 (默认: 使用配置文件中的设置)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="运行完成后显示统计信息"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="进入交互模式"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="最大迭代次数，防止无限循环 (默认: 100)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="仅验证环境和配置，不运行状态机"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="设置日志级别"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="游戏自动化系统 v2.0.0"
    )
    
    return parser


def main() -> int:
    """
    主函数
    
    Returns:
        int: 退出代码 (0表示成功，非0表示失败)
    """
    # 解析命令行参数
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # 加载配置文件
        if args.config:
            config.load_from_file(args.config)
        
        # 设置日志级别
        if args.log_level:
            config.logging.log_level = args.log_level
            # 重新初始化日志系统以应用新级别
            from logger import GameAutomationLogger
            GameAutomationLogger._initialized = False
            GameAutomationLogger()
        
        # 创建应用实例
        app = GameAutomationApp()
        
        # 仅验证模式
        if args.validate_only:
            logger.info("🔍 运行环境验证模式")
            success = app._validate_environment()
            return 0 if success else 1
        
        # 交互模式
        if args.interactive:
            app.interactive_mode()
            return 0
        
        # 正常运行模式
        success = app.run(
            initial_state=args.state,
            show_stats=args.stats,
            max_iterations=args.max_iterations
        )
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("👋 用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"💥 程序运行时发生未处理的异常: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)