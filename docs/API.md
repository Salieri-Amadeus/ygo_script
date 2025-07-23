# API 文档

游戏自动化系统 v2.0.0 API 参考文档

## 目录

- [配置模块 (config.py)](#配置模块-configpy)
- [日志模块 (logger.py)](#日志模块-loggerpy)
- [视觉模块 (vision.py)](#视觉模块-visionpy)
- [状态机模块 (state_machine.py)](#状态机模块-state_machinepy)
- [主程序 (main.py)](#主程序-mainpy)

---

## 配置模块 (config.py)

管理系统配置和设置。

### 配置类

#### `VisionConfig`
计算机视觉相关配置

**属性:**
- `threshold: float = 0.8` - 图像匹配阈值 (0.0-1.0)
- `timeout: int = 5` - 图像等待超时时间 (秒)
- `check_interval: float = 0.5` - 检查间隔 (秒)
- `retries: int = 3` - 重试次数
- `delay_between_retries: float = 2.0` - 重试间隔 (秒)
- `click_duration: float = 0.2` - 鼠标移动持续时间 (秒)
- `post_click_delay: float = 1.0` - 点击后等待时间 (秒)

#### `StateMachineConfig`
状态机相关配置

**属性:**
- `initial_state: str = "undefined_menu"` - 初始状态
- `max_stop_count: int = 5` - 最大重复次数
- `break_count: int = 8` - 最大中断次数
- `fallback_key: str = "esc"` - 失败时按键
- `state_transition_delay: float = 0.1` - 状态转换延迟 (秒)

#### `Config`
主配置类

**方法:**

##### `load_from_file(config_path: Optional[str] = None) -> bool`
从JSON文件加载配置

**参数:**
- `config_path` (str, optional): 配置文件路径

**返回:**
- `bool`: 是否成功加载

**示例:**
```python
from config import config
success = config.load_from_file("my_config.json")
```

##### `save_to_file(config_path: Optional[str] = None) -> bool`
保存配置到JSON文件

**参数:**
- `config_path` (str, optional): 配置文件路径

**返回:**
- `bool`: 是否成功保存

##### `validate() -> bool`
验证配置的有效性

**返回:**
- `bool`: 配置是否有效

##### `get_image_path(image_name: str) -> str`
获取图像文件的完整路径

**参数:**
- `image_name` (str): 图像文件名

**返回:**
- `str`: 图像文件的完整路径

---

## 日志模块 (logger.py)

提供统一的日志记录功能。

### 核心函数

#### `get_logger(name: str) -> logging.Logger`
获取日志记录器的便捷函数

**参数:**
- `name` (str): 日志记录器名称，建议使用 `__name__`

**返回:**
- `logging.Logger`: 配置好的日志记录器实例

**示例:**
```python
from logger import get_logger
logger = get_logger(__name__)
logger.info("模块初始化完成")
```

### 装饰器

#### `@log_function_call`
自动记录函数调用

**示例:**
```python
@log_function_call
def my_function(x, y):
    return x + y
```

#### `@log_execution_time`
记录函数执行时间

**示例:**
```python
@log_execution_time
def slow_function():
    time.sleep(1)
```

### 上下文管理器

#### `LogContext`
日志上下文管理器

**示例:**
```python
with LogContext("图像识别过程"):
    # 在这个代码块中的所有日志都会包含上下文信息
    logger.info("开始检测按钮")
```

---

## 视觉模块 (vision.py)

提供计算机视觉和UI交互功能。

### 数据类

#### `MatchResult`
图像匹配结果

**属性:**
- `found: bool` - 是否找到匹配
- `position: Optional[Tuple[int, int]]` - 匹配位置 (x, y)
- `confidence: float` - 匹配置信度 (0.0-1.0)
- `template_size: Tuple[int, int]` - 模板图像大小
- `match_time: float` - 匹配耗时 (秒)

#### `ClickResult`
点击操作结果

**属性:**
- `success: bool` - 是否成功点击
- `position: Tuple[int, int]` - 点击位置 (x, y)
- `click_time: float` - 点击耗时 (秒)
- `error_message: Optional[str]` - 错误信息

### 核心类

#### `ImageMatcher`
图像匹配器

**方法:**

##### `find_image(template_path: str, region: Optional[Tuple[int, int, int, int]] = None) -> MatchResult`
在屏幕上查找指定图像

**参数:**
- `template_path` (str): 模板图像文件名
- `region` (tuple, optional): 搜索区域 (x, y, width, height)

**返回:**
- `MatchResult`: 匹配结果

**示例:**
```python
from vision import ImageMatcher
matcher = ImageMatcher()
result = matcher.find_image("btn_solo.png")
if result.found:
    print(f"找到按钮，位置: {result.position}")
```

#### `MouseController`
鼠标控制器

**方法:**

##### `click(x: int, y: int, button: str = 'left') -> ClickResult`
在指定位置点击鼠标

**参数:**
- `x` (int): 点击X坐标
- `y` (int): 点击Y坐标
- `button` (str): 鼠标按钮 ('left', 'right', 'middle')

**返回:**
- `ClickResult`: 点击操作结果

#### `KeyboardController`
键盘控制器

**方法:**

##### `press_key(key, duration: float = 0.1) -> bool`
按下并释放按键

**参数:**
- `key`: 按键 (可以是Key枚举值或字符串)
- `duration` (float): 按键持续时间

**返回:**
- `bool`: 是否成功按键

##### `type_text(text: str, interval: float = 0.05) -> bool`
输入文本

**参数:**
- `text` (str): 要输入的文本
- `interval` (float): 字符间隔时间

**返回:**
- `bool`: 是否成功

#### `VisionSystem`
视觉系统主类

**方法:**

##### `find_and_click(template_path: str, retries: Optional[int] = None) -> bool`
查找图像并点击

**参数:**
- `template_path` (str): 模板图像文件名
- `retries` (int, optional): 重试次数

**返回:**
- `bool`: 是否成功找到并点击

**示例:**
```python
from vision import vision_system
success = vision_system.find_and_click("btn_solo.png", retries=3)
```

##### `wait_for_any_image(template_paths: List[str], timeout: Optional[int] = None) -> Optional[str]`
等待任意一个图像出现

**参数:**
- `template_paths` (List[str]): 模板图像文件名列表
- `timeout` (int, optional): 超时时间

**返回:**
- `str`: 首先出现的图像文件名，超时返回None

---

## 状态机模块 (state_machine.py)

实现可扩展的状态机系统。

### 枚举

#### `StateResult`
状态执行结果枚举

- `SUCCESS` - 成功执行并转换到下一状态
- `FAILED` - 执行失败
- `RETRY` - 需要重试
- `TERMINATED` - 正常终止

### 数据类

#### `StateTransition`
状态转换记录

**属性:**
- `from_state: str` - 源状态
- `to_state: Optional[str]` - 目标状态
- `timestamp: float` - 转换时间戳
- `execution_time: float` - 执行时间
- `result: StateResult` - 执行结果
- `error_message: Optional[str]` - 错误信息

### 基类

#### `BaseState`
状态基类

**抽象方法:**

##### `execute() -> Optional[str]`
执行状态逻辑

**返回:**
- `str`: 下一个状态名称，None表示结束

**生命周期方法:**

##### `on_enter() -> None`
状态进入时调用

##### `on_exit(next_state: Optional[str]) -> None`
状态退出时调用

##### `on_error(error: Exception) -> Optional[str]`
错误处理

**示例:**
```python
class MyState(BaseState):
    def __init__(self):
        super().__init__("my_state", "我的自定义状态")
    
    def execute(self) -> Optional[str]:
        # 状态逻辑
        return "next_state"
```

#### `ImageBasedState`
基于图像检测的状态

**构造函数:**
```python
def __init__(self, name: str, target_image: str, next_state: str,
             description: str = "", alternative_images: List[str] = None,
             click_offset: tuple = (0, 0), custom_timeout: int = None)
```

**示例:**
```python
state = ImageBasedState(
    name="start_menu",
    target_image="btn_solo.png",
    next_state="solo_menu",
    alternative_images=["btn_solo2.png"]
)
```

### 主类

#### `StateMachine`
状态机主类

**方法:**

##### `register_state(state: BaseState) -> None`
注册状态

**参数:**
- `state` (BaseState): 要注册的状态实例

##### `run(initial_state: Optional[str] = None, max_iterations: int = 100) -> bool`
运行状态机

**参数:**
- `initial_state` (str, optional): 初始状态
- `max_iterations` (int): 最大迭代次数

**返回:**
- `bool`: 是否正常结束

**示例:**
```python
from state_machine import state_machine
success = state_machine.run("start_menu")
```

##### `get_statistics() -> Dict[str, Any]`
获取状态机统计信息

**返回:**
- `Dict`: 包含各种统计信息的字典

### 装饰器

#### `@state(name: str)`
状态注册装饰器（兼容性）

**示例:**
```python
@state("my_state")
def handle_my_state():
    return "next_state"
```

---

## 主程序 (main.py)

应用入口和命令行接口。

### 主类

#### `GameAutomationApp`
游戏自动化应用主类

**方法:**

##### `run(initial_state: Optional[str] = None, show_stats: bool = False, max_iterations: int = 100) -> bool`
运行游戏自动化系统

**参数:**
- `initial_state` (str, optional): 初始状态
- `show_stats` (bool): 是否显示统计信息
- `max_iterations` (int): 最大迭代次数

**返回:**
- `bool`: 是否成功运行

##### `interactive_mode() -> None`
交互模式，允许用户通过命令行交互控制系统

### 命令行接口

#### 基本用法
```bash
python main.py                        # 使用默认配置运行
python main.py --config custom.json   # 使用自定义配置文件
python main.py --state start_menu     # 从指定状态开始
python main.py --stats                # 运行完成后显示统计信息
python main.py --interactive          # 进入交互模式
```

#### 参数说明

- `--config, -c`: 配置文件路径
- `--state, -s`: 初始状态名称
- `--stats`: 运行完成后显示统计信息
- `--interactive, -i`: 进入交互模式
- `--max-iterations`: 最大迭代次数
- `--validate-only`: 仅验证环境和配置
- `--log-level`: 设置日志级别
- `--version, -v`: 显示版本信息

---

## 使用示例

### 基本使用

```python
# 导入必要模块
from config import config
from logger import get_logger
from vision import vision_system
from state_machine import state_machine, ImageBasedState

# 获取日志记录器
logger = get_logger(__name__)

# 加载配置
config.load_from_file("my_config.json")

# 创建自定义状态
custom_state = ImageBasedState(
    name="custom_menu",
    target_image="btn_custom.png", 
    next_state="next_menu",
    description="自定义菜单状态"
)

# 注册状态
state_machine.register_state(custom_state)

# 运行状态机
success = state_machine.run("custom_menu")
```

### 创建自定义状态

```python
from state_machine import BaseState
from vision import vision_system

class ComplexState(BaseState):
    def __init__(self):
        super().__init__("complex_state", "复杂状态处理")
    
    def execute(self) -> Optional[str]:
        # 复杂的状态逻辑
        if vision_system.is_image_present("condition1.png"):
            vision_system.find_and_click("button1.png")
            return "state_a"
        elif vision_system.is_image_present("condition2.png"):
            vision_system.find_and_click("button2.png")
            return "state_b"
        else:
            return None  # 结束状态机
    
    def on_error(self, error: Exception) -> Optional[str]:
        self.logger.error(f"复杂状态发生错误: {error}")
        # 自定义错误恢复
        vision_system.keyboard.press_key("escape")
        return "safe_state"

# 注册状态
state_machine.register_state(ComplexState())
```

### 配置管理

```python
from config import config

# 修改配置
config.vision.threshold = 0.9
config.vision.timeout = 10
config.state_machine.max_stop_count = 3

# 保存配置
config.save_to_file("updated_config.json")

# 验证配置
if config.validate():
    print("配置有效")
```

---

## 错误处理

### 常见异常

- `FileNotFoundError`: 图像文件不存在
- `TimeoutError`: 操作超时
- `ConfigurationError`: 配置错误
- `StateNotFoundError`: 状态不存在

### 最佳实践

1. **总是使用日志记录器**:
```python
logger = get_logger(__name__)
logger.info("操作开始")
```

2. **适当设置超时时间**:
```python
config.vision.timeout = 10  # 根据需要调整
```

3. **使用上下文管理器**:
```python
with LogContext("图像识别"):
    result = vision_system.find_and_click("button.png")
```

4. **验证环境**:
```python
if not config.validate():
    logger.error("配置验证失败")
    exit(1)
```

---

## 扩展指南

### 添加新的视觉功能

```python
from vision import VisionSystem

class CustomVisionSystem(VisionSystem):
    def find_text(self, text: str) -> bool:
        # 实现文本识别功能
        pass
```

### 创建插件系统

```python
from state_machine import BaseState

class PluginState(BaseState):
    def __init__(self, plugin_config):
        super().__init__(plugin_config.name, plugin_config.description)
        self.plugin_config = plugin_config
    
    def execute(self) -> Optional[str]:
        # 插件逻辑
        pass
```

---

## 版本历史

- **v2.0.0** (2024-12): 模块化重构，添加完整的配置系统和日志系统
- **v1.0.0** (2024-11): 初始版本，基本的状态机功能