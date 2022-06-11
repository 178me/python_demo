import pyautogui
import os
import pyperclip
from time import sleep, time
from lib import log

class AutoMationModule:
    def __init__(self):
        self.debug_mode = True
        self.index = "Root"
        self.res_path = os.path.join(os.getcwd(), "src")
        self.auto = pyautogui

    def pretreatment(self):
        pass

    def exit(self):
        pass

    def dl(self, message):
        if self.debug_mode:
            log.info(f"{self.index}调试信息: {message}")

    def save_errpage(self):
        self.auto.screenshot(os.path.join(
            self.res_path, "errpage", f"{self.index}.png"))

    def get_window_size(self):
        pass

    def ocr(self, x1=0, y1=0, x2=2000, y2=2000, color_format="000000-101010", sim=0.99, find_time=3):
        pass

    def get_keyboard_keys(self):
        return self.auto.KEYBOARD_KEYS

    def find_image(self, pic_name, find_time=3, offset=(0, 0), is_click=False, x1=0, y1=0, x2=2000, y2=2000, grayscale=False, sim=0.9, **option):
        pic_name = self.res_path + os.sep + pic_name
        timeout = time() + find_time
        point = []
        while timeout > time():
            self.pretreatment()
            point = list(self.auto.locateAll(pic_name, self.auto.screenshot(
            ),grayscale=grayscale, confidence=sim, region=(x1, y1, x2-x1, y2-y1)))
            if point:
                point = point[0]
                break
        if not point:
            return None
        if is_click:
            click_pos = pyautogui.center(point)
            self.click(click_pos.x + offset[0], click_pos.y + offset[1], **option)
        return point

    def find_images(self, pic_name, find_time=3, x1=0, y1=0, x2=2000, y2=2000, sim=0.8,grayscale=False):
        pic_name = self.res_path + os.sep + pic_name
        timeout = time() + find_time
        point = []
        while timeout > time():
            self.pretreatment()
            point = list(self.auto.locateAll(pic_name, self.auto.screenshot(
            ),grayscale=grayscale, confidence=sim, region=(x1, y1, x2-x1, y2-y1)))
            if point:
                break
        if not point:
            return None
        return point

    def is_disappear_by_image(self, pic_name, search_time=5, find_time=0.5, **find_iamge_param):
        pass

    def click(self, x, y, button="left", click_count=1, interval=0.1, click_delay=0.1):
        self.auto.click(x=x, y=y, clicks=click_count,
                        interval=interval, button=button)
        sleep(click_delay)

    def move(self, x, y,**option):
        self.auto.moveTo(x,y,**option)

    def drag(self, x1, y1, x2, y2, duration, **option):
        self.auto.moveTo(x1, y1)
        self.auto.dragTo(x2, y2, duration=duration, **option)

    def input_text(self, text):
        pyperclip.copy(text)
        self.hot_key("ctrl", "v")

    def hot_key(self, *args, **kwargs):
        self.auto.hotkey(*args, **kwargs)

    def press(self, *args, **kwargs):
        self.auto.press(*args, **kwargs)


if __name__ == "__main__":
    print("自动化测试")
    auto = AutoMationModule()
    #  auto.click(1157,450)
    #  for _ in range(18):
        #  auto.click(616,358,click_count=2)
        #  sleep(1.5)
    #  auto.input_text("你好呀")

    pyautogui.confirm
