# 游戏自动化脚本

这是一个基于计算机视觉的游戏自动化脚本，使用状态机模式来导航游戏菜单并自动执行操作。

## 🚀 功能特性

### 🆕 v2.0 新架构特性
- **模块化设计**: 将功能拆分为独立的模块，便于维护和扩展
- **配置管理**: 支持JSON配置文件，集中管理所有参数
- **完整日志系统**: 多级别日志记录，支持文件轮转和彩色输出
- **交互模式**: 提供命令行交互界面，便于调试和控制
- **统计分析**: 详细的执行统计和性能分析
- **API文档**: 完整的API参考文档和使用示例
- **类型注解**: 全面的类型提示，提高代码可维护性
- **错误恢复**: 增强的错误处理和自动恢复机制

### 🔧 核心功能
- **状态机导航**: 使用状态机模式自动在不同游戏菜单之间导航
- **计算机视觉**: 通过图像识别检测UI元素并执行操作
- **错误恢复**: 内置重试机制和错误处理
- **实时屏幕监控**: 使用MSS库进行高效屏幕截图
- **自动点击**: 自动定位并点击游戏按钮

## 📋 系统要求

- Python 3.6+
- 支持的操作系统: Windows, macOS, Linux
- 游戏需要在主显示器上运行

## 🛠️ 依赖库

```bash
pip install opencv-python
pip install numpy
pip install pyautogui
pip install mss
pip install pynput
```

## 📁 项目结构

```
.
├── main.py              # 主程序入口 (v2.0新架构)
├── config.py            # 配置管理模块
├── logger.py            # 日志系统模块
├── vision.py            # 计算机视觉模块 (重构版)
├── state_machine.py     # 状态机模块 (重构版)
├── test.py              # 原始程序文件 (兼容性保留)
├── vision_utils.py      # 原始视觉工具 (兼容性保留)
├── images/              # UI元素截图文件夹
│   ├── btn_solo.png     # 单人游戏按钮
│   ├── btn_train.png    # 训练按钮
│   ├── btn_challenge.png # 挑战按钮
│   ├── btn_play.png     # 开始游戏按钮
│   ├── btn_level.png    # 关卡选择按钮
│   └── ...              # 其他UI元素
├── logs/                # 日志文件目录 (自动创建)
├── docs/                # 文档目录
│   └── API.md           # API 参考文档
├── config.json          # 配置文件 (可选)
├── requirements.txt     # 依赖库清单
├── README.md            # 项目说明文档
└── TODO.md              # 开发任务清单
```

## 🎮 支持的游戏状态

脚本支持以下游戏状态的自动导航：

1. **start_menu** - 开始菜单
2. **solo_menu** - 单人游戏菜单  
3. **train_menu** - 训练菜单
4. **challenge_menu** - 挑战菜单
5. **sp_challenge_menu** - 特殊挑战菜单
6. **level_menu** - 关卡选择菜单
7. **play_menu** - 游戏进行中
8. **undefined_menu** - 未知状态（用于错误恢复）

## 🚀 使用方法

### 🔧 安装和配置

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **启动游戏**: 确保游戏在主显示器上运行

### 📱 新架构使用 (推荐 v2.0)

3. **基本运行**:
   ```bash
   python main.py                        # 使用默认配置运行
   python main.py --config custom.json   # 使用自定义配置文件
   python main.py --state start_menu     # 从指定状态开始
   python main.py --stats                # 运行完成后显示统计信息
   ```

4. **交互模式**:
   ```bash
   python main.py --interactive          # 进入交互控制模式
   ```

5. **环境验证**:
   ```bash
   python main.py --validate-only        # 仅验证环境，不运行
   ```

### 🔄 兼容性使用 (原版本)

6. **运行原版脚本**:
   ```bash
   python test.py                        # 运行原始版本
   ```

## ⚙️ 配置选项

### 💻 新架构配置 (v2.0)

系统支持JSON配置文件，可以集中管理所有参数：

**创建配置文件** `config.json`:
```json
{
  "vision": {
    "threshold": 0.8,
    "timeout": 5,
    "check_interval": 0.5,
    "retries": 3,
    "delay_between_retries": 2.0,
    "click_duration": 0.2,
    "post_click_delay": 1.0
  },
  "state_machine": {
    "initial_state": "undefined_menu",
    "max_stop_count": 5,
    "break_count": 8,
    "fallback_key": "esc",
    "state_transition_delay": 0.1
  },
  "paths": {
    "images_dir": "images",
    "logs_dir": "logs",
    "config_file": "config.json"
  },
  "logging": {
    "log_level": "INFO",
    "max_log_size": 10485760,
    "backup_count": 5
  }
}
```

**主要配置参数说明:**
- `vision.threshold`: 图像匹配阈值 (0.0-1.0)
- `vision.timeout`: 图像等待超时时间 (秒)
- `state_machine.max_stop_count`: 最大重复状态次数
- `state_machine.break_count`: 最大中断次数
- `logging.log_level`: 日志级别 (DEBUG/INFO/WARNING/ERROR)

### 🔄 原版配置

在 `test.py` 中可以调整以下参数：
- `max_stop_cpt = 5`: 最大重复状态次数
- `break_cpt = 8`: 最大中断次数  
- `threshold=0.8`: 图像匹配阈值
- `timeout=5`: 图像等待超时时间（秒）

## 🔧 自定义配置

### 添加新状态

1. 在 `test.py` 中使用 `@state("state_name")` 装饰器定义新状态处理函数
2. 添加相应的UI元素截图到 `images/` 文件夹
3. 在状态处理函数中调用 `vu.wait_for_image()` 检测UI元素

示例：
```python
@state("new_menu")
def handle_new_menu():
    print("📘 当前状态: new_menu")
    if vu.wait_for_image("images/btn_new.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_new.png"))
        time.sleep(1)
        return "next_state"
    return "undefined_menu"
```

### 更新UI元素

如果游戏UI发生变化，需要重新截图并替换 `images/` 文件夹中的相应文件。

## 🐛 故障排除

### 常见问题

1. **图像识别失败**
   - 检查图像文件是否存在
   - 调整匹配阈值 (`threshold`)
   - 确保游戏分辨率与截图一致

2. **脚本卡住**
   - 脚本内置重试机制，会自动尝试恢复
   - 手动按 ESC 键返回主菜单

3. **点击位置不准确**
   - 检查屏幕缩放设置
   - 确保游戏在主显示器上运行

### 调试模式

在 `vision_utils.py` 中启用详细日志输出：
- 函数会打印检测状态和点击位置
- 观察控制台输出了解脚本行为

## ⚠️ 注意事项

- **使用风险**: 此脚本仅供学习和研究目的
- **游戏政策**: 使用前请查看游戏的自动化使用政策
- **安全性**: 脚本会控制鼠标和键盘，运行时请注意
- **性能**: 持续运行可能消耗系统资源

## 🤝 贡献

欢迎提交问题报告和功能请求！

## 📄 许可证

本项目仅供学习和研究使用。

---

**重要提醒**: 请遵守相关游戏的使用条款，合理使用自动化脚本。