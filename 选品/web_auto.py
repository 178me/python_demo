import os
if os.name == "nt":
    import win32com.client
from time import time, sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


class WebAutoModule:
    def __init__(self) -> None:
        self.By = By
        self.init_driver(12306)

    def init_driver(self, port=None, browser_name="360安全浏览器"):
        try:
            options = Options()
            if port:
                options.add_experimental_option(
                    "debuggerAddress", f"127.0.0.1:{port}")
            if os.name == "nt":
                browser_path = self.get_browser_path(browser_name)
                options.binary_location = browser_path
                self.driver = webdriver.Chrome(
                    "./input/chromedriver.exe", options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(e)
            raise Exception(f"{browser_name} 连接失败!")
        print(f"{browser_name} 连接成功!")

    def quit(self):
        self.driver.quit()

    def get_browser_path(self, browser_name):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            path = os.path.join(os.path.expanduser(r'~'), "Desktop")
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    if browser_name in filename:
                        path = dirpath + "\\" + filename
            shortcut = shell.CreateShortCut(path).TargetPath
            return shortcut
        except Exception as e:
            print(e)
            raise Exception(f"{browser_name}路径查找失败")

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
            elem.click()
        return elem

    def find_elems(self, xpath, find_time=3):
        timeout = time() + find_time
        elem_list = (-1, -1, -1)
        while timeout > time():
            elem_list = self.driver.find_elements(By.XPATH, xpath)
            if elem_list:
                break
        if not elem_list:
            return []
        return elem_list

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

    def click(self, x, y, button="left", click_delay=0.1):
        x = int(x)
        y = int(y)
        if button == "left":
            ActionChains(self.driver).move_by_offset(x, y).click().perform()
        else:
            ActionChains(self.driver).move_by_offset(
                x, y).context_click().perform()
        ActionChains(self.driver).move_by_offset(-x, -y).perform()
        sleep(click_delay)

    def input_text(self, elem, text, is_clear=True, is_submit=False):
        if is_clear:
            elem.clear()
        elem.send_keys(text)
        if is_submit:
            elem.submit()

    def hi(self, elem):
        self.driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            elem,
            "border: 2px solid red;"  # 边框border:2px;
        )

    def open_url(self, url, wait_time=5):
        self.driver.implicitly_wait(wait_time)
        if url != self.driver.current_url:
            self.driver.get(url)


if __name__ == "__main__":
    print("网页模块测试")
    run = WebAutoModule()
    elem = run.find_elem("//*[@class='b_searchboxSubmit']")
    pos = run.get_center_pos(elem)
    run.click(pos.get("center_x"), pos.get("center_y"))
    run.quit()
