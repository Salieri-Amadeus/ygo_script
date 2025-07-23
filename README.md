# 游戏自动化脚本

这是一个基于计算机视觉的游戏自动化脚本，使用状态机模式来导航游戏菜单并自动执行操作。

## 🚀 功能特性

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
├── test.py              # 主程序文件，包含状态机逻辑
├── vision_utils.py      # 计算机视觉工具函数
├── images/              # UI元素截图文件夹
│   ├── btn_solo.png     # 单人游戏按钮
│   ├── btn_train.png    # 训练按钮
│   ├── btn_challenge.png # 挑战按钮
│   ├── btn_play.png     # 开始游戏按钮
│   ├── btn_level.png    # 关卡选择按钮
│   └── ...              # 其他UI元素
└── README.md            # 项目说明文档
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

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **启动游戏**: 确保游戏在主显示器上运行

3. **运行脚本**:
   ```bash
   python test.py
   ```

4. **监控输出**: 脚本会在控制台显示当前状态和操作

## ⚙️ 配置选项

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