import pyperclip
from lib import WindowSelector, log, Images, sleep


class XLZ:
    def __init__(self, app):
        self.images = Images(app)
        self.ws = WindowSelector()

    def connect(self):
        try:
            self.ws.connect(0, title_re=".*小栗子框架.*")
        except Exception as e:
            log.exception(e)
            log.warning("连接窗口出错")

    def bulk_import_qq(self, qq_number_text):
        task_name = "批量导入QQ号码"
        log.info(f"{task_name} 开始")
        try:
            pyperclip.copy(qq_number_text)
            self.ws.set_window(title_re=".*小栗子框架.*")
            list_view = self.ws.find_element_in_app(
                class_name_re="SysListView32", control_id=230)  # 230
            list_view.show()
            sleep(1)
            list_view.element.click_input(coords=(10, 30), button="right")
            popup_menu = self.ws.find_element_in_windows(
                friendly_class_name="PopupMenu")
            sleep(0.5)
            popup_menu.element.menu().item("批量导入 -> 剪贴板导入").click_input()
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def login_select_qq(self, qq_number):
        task_name = "登录选中QQ"
        log.info(f"{task_name} 开始")
        try:
            self.load_window_close()
            sleep(1)
            self.ws.set_window(title_re=".*小栗子框架.*")
            list_view = self.ws.find_element_in_app(
                class_name_re="SysListView32", control_id=230)  # 230
            list_view.show()
            sleep(1)
            subitem = self.get_subitem("Uin", list_view.element.columns())
            list_view.element.get_item(
                qq_number, subitem).click_input(button="right")
            popup_menu = self.ws.find_element_in_windows(
                friendly_class_name="PopupMenu")
            sleep(1)
            popup_menu.element.menu().item("登录选中QQ").click_input()
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def get_subitem(self, text, columns):
        task_name = "获取Sublime"
        log.info(f"{task_name} 开始")
        try:
            for column in columns:
                if text in column["text"]:
                    return column['subitem']
            return 1
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def load_window_close(self):
        task_name = "取消二维码"
        log.info(f"{task_name} 开始")
        try:
            self.ws.set_window(title_re=".*加载.*")
            load_window = self.ws.find_element_in_app()
            load_window.close_window()
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def load_window_screenshot(self, qq_number):
        task_name = "记录登录二维码"
        log.info(f"{task_name} 开始")
        try:
            self.ws.set_window(title_re=".*加载.*")
            load_window = self.ws.find_element_in_app()
            self.images.window_screenshot(load_window, f"{qq_number}.png")
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False


if __name__ == "__main__":
    print("小栗子框架 自动化测试")
    import sys
    from PyQt5.Qt import (QApplication)
    app = QApplication(sys.argv)
    xlz = XLZ(app)
    xlz.connect()
    # xlz.login_select_qq('466649662')
    #  xlz.login_select_qq("142191l392")
    xlz.load_window_screenshot('466649662')
