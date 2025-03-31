import time
import vision_utils as vu
from pynput.keyboard import Key
import pyautogui

# 状态处理函数表
state_handlers = {}

# 注册状态的装饰器
def state(name):
    def decorator(func):
        state_handlers[name] = func
        return func
    return decorator

# 当前状态
current_state = "undefined_menu"

# 状态处理函数们 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

@state("start_menu")
def handle_start_menu():
    print("📘 当前状态: start_menu")
    if vu.wait_for_image("images/btn_solo.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_solo.png"))
        time.sleep(1)
        return "solo_menu"
    elif vu.wait_for_image("images/btn_solo2.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_solo2.png"))
        time.sleep(1)
        return "solo_menu"
    return "undefined_menu"

@state("solo_menu")
def handle_solo_menu():
    print("📘 当前状态: solo_menu")
    if vu.wait_for_image("images/btn_train.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_train.png"))
        time.sleep(1)
        return "train_menu"
    return "undefined_menu"

@state("train_menu")
def handle_train_menu():
    print("📘 当前状态: train_menu")
    if vu.wait_for_image("images/btn_challenge.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_challenge.png"))
        time.sleep(1)
        return "challenge_menu"
    return "undefined_menu"

@state("challenge_menu")
def handle_challenge_menu():
    print("📘 当前状态: challenge_menu")
    if vu.wait_for_image("images/btn_play.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_play.png"))
        time.sleep(1)
        return "sp_challenge_menu"
    return "undefined_menu"

@state("sp_challenge_menu")
def handle_sp_challenge_menu():
    print("📘 当前状态: sp_challenge_menu")
    if vu.wait_for_image("images/btn_level.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_level.png"))
        time.sleep(1)
        return "level_menu"
    return "undefined_menu"

@state("level_menu")
def handle_level_menu():
    print("📘 当前状态: level_menu")
    if vu.wait_for_image("images/btn_play.png", threshold=0.8, timeout=5):
        vu.move_and_click(*vu.robust_wait_image("images/btn_play.png"))
        time.sleep(1)
        return "play_menu"
    return "undefined_menu"

@state("play_menu")
def handle_play_menu():
    print("📘 当前状态: play_menu")
    return None

@state("undefined_menu")
def handle_undefined_menu():
    print("📘 当前状态: undefined_menu")
    pyautogui.moveTo(10, 10, duration=0.2)
    if vu.wait_for_image("images/btn_solo.png", threshold=0.8, timeout=1):
        print("🔍 检测到 btn_solo.png → 回到 start_menu")
        return "start_menu"

    elif vu.wait_for_image("images/btn_train.png", threshold=0.8, timeout=1):
        print("🔍 检测到 btn_train.png → 回到 solo_menu")
        return "solo_menu"

    elif vu.wait_for_image("images/train_menu.png", threshold=0.8, timeout=1):
        print("🔍 检测到 train_menu.png → 回到 train_menu")
        return "train_menu"

    else:
        print("❌ 无法判断当前界面，按 ESC 并保留在 undefined_menu")
        vu.press_key(Key.esc)
        time.sleep(1)
        return "undefined_menu"


# 主循环 ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

visited = set()
stop_cpt = 0
max_stop_cpt = 5  # 最大重复次数
break_cpt = 8  # 最大中断次数
while current_state:
    if current_state in visited:
        print("🔁 状态重复，可能卡住了")
        print("停止计数器:", stop_cpt)
        stop_cpt += 1
        if stop_cpt >= max_stop_cpt:
            print("⛔ 达到最大重复次数，尝试按 ESC 键")
            vu.press_key(Key.esc)
            time.sleep(1)
        if stop_cpt >= break_cpt:
            print("⛔ 达到最大中断次数，退出程序")
            break
    else:
        stop_cpt = 0  # 重置计数器
    visited.add(current_state)


    handler = state_handlers.get(current_state)
    if handler is None:
        print(f"❌ 状态 '{current_state}' 没有定义处理函数")
        break
    next_state = handler()
    current_state = next_state
