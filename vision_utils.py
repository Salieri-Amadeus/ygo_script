import cv2
import numpy as np
import pyautogui
import time
import mss
from pynput.keyboard import Controller
from pynput.keyboard import Key

keyboard = Controller()

def wait_for_image(template_path, threshold=0.8, timeout=30, check_interval=0.5):
    template = cv2.imread(template_path, 0)
    if template is None:
        raise FileNotFoundError(f"❌ 无法加载图像 {template_path}")
    w, h = template.shape[::-1]
    start_time = time.time()

    with mss.mss() as sct:
        while True:
            if time.time() - start_time > timeout:
                return None
            monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            gray_screen = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(gray_screen, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= threshold)
            for pt in zip(*locations[::-1]):
                return pt[0] + w // 2, pt[1] + h // 2
            time.sleep(check_interval)

def press_key(key):
    keyboard.press(key)
    keyboard.release(key)

def robust_wait_image(template_path, threshold=0.8, timeout=30, check_interval=0.5,
                      retries=3, fallback_key=Key.esc, delay_between_retries=2):
    """等待图像出现，失败时尝试按键并重试"""
    attempt = 0
    while attempt < retries:
        print(f"🔎 第 {attempt + 1} 次尝试检测图像：{template_path}")
        result = wait_for_image(template_path, threshold, timeout, check_interval)
        if result:
            print(f"✅ 成功检测到图像 {template_path}，位置：{result}")
            return result
        else:
            print(f"❌ 第 {attempt + 1} 次失败，按下 {fallback_key} 键重试…")
            press_key(fallback_key)
            time.sleep(delay_between_retries)
            attempt += 1
    print(f"⛔ 达到最大重试次数，仍未检测到图像 {template_path}")
    return None

def move_and_click(x, y):
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()
    print(f"🖱️ 点击位置：({x}, {y})")
