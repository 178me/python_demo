import os
import re
if os.name == "nt":
    import win32com.client
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging
log = logging.getLogger('日志')
from lib_178me.other import Other


class WebAutoModule:
    def __init__(self, browser_name="") -> None:
        self.By = By
        self.Keys = Keys
        self.init_driver(12306, browser_name)

    def init_driver(self, port=12306, browser_name=""):
        try:
            options = Options()
            # netstat -ano | findstr 5003  查看端口使用情况
            if os.name == "nt":
                self.browser_path = self.get_browser_path(browser_name)
                self.browser_path = self.browser_path.replace(" (x86)", "")
                current_port = self.get_browser_port()
                if not current_port:
                    self.open_browser(f"--remote-debugging-port={port}")
                else:
                    port = current_port
                options.add_experimental_option("debuggerAddress",
                                                f"127.0.0.1:{port}")
                options.binary_location = self.browser_path
                self.driver = webdriver.Chrome(
                    "./res/chromedriver.exe", options=options)
            else:
                browser_name = "Chrome"
                options.add_experimental_option("debuggerAddress",
                                                f"127.0.0.1:{port}")
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            log.exception(e)
            raise Exception(f"{browser_name} 连接失败!")
        log.debug(f"{browser_name} 连接成功!")

    def get_browser_port(self):
        result = Other.exec_command("tasklist")
        pid_list = []
        for r in result.split("\n"):
            if "chrome.exe" in r:
                pid_list.append(int(re.split(" +", r)[1]))
        result = Other.exec_command("netstat -ano")
        port_list = []
        for r in result.split("\n")[4:]:
            r = re.split(" +", r)
            if len(r) < 4:
                continue
            if int(r[-1]) in pid_list:
                if "127.0.0.1" not in r[2]:
                    continue
                port = int(r[2].split(":")[1])
                port_list.append(port)
        if not port_list:
            return None
        return port_list[0]

    def get_browser_path(self, browser_name):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            path = os.path.join(os.path.expanduser(r'~'), "Desktop")
            for dirpath, _, filenames in os.walk(path):
                if "Desktop" not in dirpath.split(os.sep)[-1]:
                    continue
                for filename in filenames:
                    if "lnk" not in filename.split(".")[-1]:
                        continue
                    if browser_name in filename:
                        path = dirpath + "\\" + filename
                        break
                break
            shortcut = shell.CreateShortCut(path).TargetPath
            return shortcut
        except Exception as e:
            log.exception(e)
            raise Exception(f"{browser_name}路径查找失败")

    def open_browser(self, *args):
        Other.open_app(self.browser_path, *args)

    def quit(self):
        self.driver.quit()

    def close(self):
        self.driver.close()

    def js_find_elem(self, js_code, find_time=3, is_click=False):
        timeout = time() + find_time
        elem = None
        js_code = "return " + js_code
        while timeout > time():
            elem = self.driver.execute_script(js_code)
            if elem:
                break
        if not elem:
            return None
        if is_click and elem.is_displayed:
            self.click_elem(elem)
        return elem

    def find_elem(self, xpath, find_time=3, is_click=False):
        timeout = time() + find_time
        elem_list = (-1, -1, -1)
        while timeout > time():
            elem_list = self.driver.find_elements(By.XPATH, xpath)
            if elem_list:
                break
        if not elem_list:
            return None
        elem = elem_list[0]
        if is_click and elem.is_displayed:
            self.click_elem(elem)
        return elem

    def find_elems(self, xpath, find_time=3):
        timeout = time() + find_time
        elem_list = []
        while timeout > time():
            elem_list = self.driver.find_elements(By.XPATH, xpath)
            if elem_list:
                break
        if not elem_list:
            return []
        return elem_list

    def click_elem(self, elem):
        try:
            elem.click()
            return True
        except Exception as e:
            log.error("点击失败")
        return False

    def get_center_pos(self, elem):
        left = elem.location.get("x")
        top = elem.location.get("y")
        height = elem.size.get("height")
        width = elem.size.get("width")
        center_x = left + int(width / 2)
        center_y = top + int(height / 2)
        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height,
            "center_x": center_x,
            "center_y": center_y
        }

    def press(self, elem, key):
        elem.send_keys(key)

    def click(self, point, button="left", click_delay=0.1):
        if not isinstance(point, tuple):
            point = self.get_center_pos(point)
            point = (point["center_x"], point["center_y"])
        if button == "left":
            ActionChains(self.driver).move_by_offset(
                point[0], point[1]).click().perform()
        else:
            ActionChains(self.driver).move_by_offset(
                point[0], point[1]).context_click().perform()
        ActionChains(self.driver).move_by_offset(-point[0],
                                                 -point[1]).perform()
        sleep(click_delay)

    def input_text(self, elem, text, is_clear=True, is_submit=False, backspace_count=0):
        try:
            if not elem.is_displayed():
                return False
            if is_clear:
                elem.clear()
            if backspace_count != 0:
                for _ in range(backspace_count):
                    elem.send_keys(self.Keys.BACKSPACE)
            elem.send_keys(str(text))
            if is_submit:
                elem.send_keys(self.Keys.ENTER)
        except:
            raise Exception("输入失败")

    def hi(self, elem):
        self.driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            elem,
            "border: 2px solid red;"  # 边框border:2px;
        )

    def open_url(self, url, wait_time=5, force_refresh=False):
        self.driver.implicitly_wait(wait_time)
        if force_refresh or url != self.driver.current_url:
            self.driver.get(url)

    def close_other_window(self, current_window):
        ''' 关闭其他窗口
        :param current_window: 需要保留的窗口句柄
        :return: None
        '''
        all_handle = self.driver.window_handles
        for handle in all_handle:
            if handle != current_window:
                self.driver.switch_to.window(handle)
                self.close()
        self.driver.switch_to.window(current_window)

    def switch_to(self, url=None, title=None, handle=None, find_time=1):
        timeout = time() + find_time
        while timeout > time():
            windows = self.get_all_window()
            for window in windows:
                if url and url in window["url"]:
                    pass
                elif title and title in window["title"]:
                    pass
                elif handle and handle == window["handle"]:
                    pass
                else:
                    continue
                self.driver.switch_to.window(window["handle"])
                return True
            sleep(0.5)
        log.debug("切换失败")
        return False

    def get_all_window(self):
        windows = []
        current_window = self.driver.current_window_handle
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            windows.append({
                "url": self.driver.current_url,
                "title": self.driver.title,
                "handle": handle,
            })
        self.driver.switch_to.window(current_window)
        return windows

    def main(self):
        sleep(0.01)


if __name__ == "__main__":
    log.debug("网页模块测试")
    run = WebAutoModule("Chrome")
    run.main()
    run.quit()
