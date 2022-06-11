import subprocess
import os
import win32com.client
from lib import WindowSelector, log,  sleep, UtilsPos


class LeiDian:
    def __init__(self):
        self.ws = WindowSelector()
        self.utils = UtilsPos()
        self.exec_path = None
        self.list2 = None
        self.server_code = None
        self.qq_account_pwd_list = None
        self.find_leidian_path()
        self.get_ld_status()

    def connect(self, index):
        try:
            index = int(index)
            self.get_ld_status()
            self.ws.connect(0, handle=int(self.list2[index][2]))
            self.ws.set_window(handle=int(self.list2[index][2]))
        except Exception as e:
            log.exception(e)
            log.warning("连接窗口出错")

    def find_leidian_path(self):
        task_name = "查找雷电模拟器启动路径"
        log.info(f"{task_name} 开始")
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            path = os.path.join(os.path.expanduser(r'~'),
                                "Desktop\\雷电多开器4.lnk")
            log.info(f"查找路径: {path}")
            shortcut = shell.CreateShortCut(path).TargetPath
            shortcut = os.path.dirname(shortcut)
            self.exec_path = str(shortcut) + "\\ldconsole.exe"
            #  self.exec_path = r'D:\leidian\LDPlayer4.0' + r'\ldconsole.exe'
            if "LeiDian" not in self.exec_path:
                raise Exception("雷电模拟器路径查找失败")
            log.info(self.exec_path)
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def console_base_command(self, command):
        """ 雷电控制台基础命令 """
        log.info(f"{self.exec_path}\\ldconsole.exe {command}")
        result = subprocess.check_output(
            f"{self.exec_path}\\ldconsole.exe {command}", timeout=10, encoding="gbk")
        log.info(result)
        return result

    def get_ld_status(self):
        task_name = "获取模拟器状态"
        log.info(f"{task_name} 开始")
        try:
            mnq_list = self.console_base_command("list2").split("\n")
            mnq_list.pop()
            for index, value in enumerate(mnq_list):
                mnq_list[index] = value.split(",")
            log.info("获取模拟器状态成功")
            return mnq_list
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def get_qq_number(self, index):
        task_name = "获取QQ号码"
        log.info(f"{task_name} 开始")
        try:
            log.info(self.list2[index])
            if self.list2[index][4] == '1':
                qq_number = self.console_base_command(
                    f'adb --index {index} --command "shell cat /sdcard/qqNumber.txt"')
                if "No such file or" in qq_number:
                    log.info("没有QQ号信息")
                    return str(index)
                qq_number = qq_number.split('----')[0]
                if not self.server_code:
                    self.server_code = qq_number.split('----')[1]
                log.info(f'雷电模拟器{index} QQ号码: {qq_number}')
                log.info('')
                return qq_number
            else:
                log.info("模拟器没有启动")
            return str(index)
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def get_all_qq_number(self):
        task_name = "获取所有QQ号码"
        log.info(f"{task_name} 开始")
        try:
            all_qq_number = ""
            if not self.list2:
                self.get_ld_status()
            all_info = ""
            for i in range(1, len(self.list2)):
                qq_number = self.get_qq_number(i)
                all_info = f'{qq_number}----{self.server_code}----{i}'
                all_qq_number += qq_number + "----$空$----5\r\n"
            if self.server_code:
                file_write_path = os.path.join(os.path.expanduser(
                    r'~'), "Desktop\\"+self.server_code+".txt")
                log.info("保存登录信息到桌面")
                with open(file_write_path, 'w') as file_writer:
                    file_writer.write(all_info)
            return all_qq_number
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def ld_scan(self, index, qr_code_path=None):
        task_name = "QQ扫码"
        log.info(f"{task_name} 开始")
        try:
            if not qr_code_path:
                qr_code_path = os.getcwd() + '\\image\\' + self.get_qq_number(index) + '.png'
            log.info(qr_code_path)
            result = self.console_base_command(
                f'scan --index {index} --file {qr_code_path}')
            if "adb" in result:
                return False
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            raise Exception('雷电扫码出错')

    def get_qq_account_pwd_list(self):
        task_name = "获取QQ账号密码列表"
        log.info(f"{task_name} 开始")
        try:
            path = os.path.join(os.path.expanduser(r'~'), "Desktop")
            qq_account_pwd_path = None
            qq_account_pwd_text = None
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if "号机" in filename:
                        qq_account_pwd_path = dirpath + "\\" + filename
            if not qq_account_pwd_path:
                raise Exception("没有找到账号密码文件!")
            with open(qq_account_pwd_path, 'r', encoding='utf-8') as file_reader:
                qq_account_pwd_text = file_reader.read()
            self.qq_account_pwd_list = qq_account_pwd_text.replace(
                "\r", "").split("\n")
            log.info(self.qq_account_pwd_list)
            self.save_qq_account_pwd_list(qq_account_pwd_path)
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def save_qq_account_pwd_list(self, qq_account_pwd_path):
        task_name = "保存QQ账号密码"
        log.info(f"{task_name} 开始")
        try:
            i = 0
            for text in self.qq_account_pwd_list:
                if len(text) < 5:
                    continue
                text = text.split("----")
                if len(text) < 3:
                    self.qq_account_pwd_list[i] += f"----{i+1}"
                i += 1
            qq_account_pwd_text = "\n".join(self.qq_account_pwd_list)
            with open(qq_account_pwd_path, 'w', encoding="utf-8") as file_writer:
                file_writer.write(qq_account_pwd_text)
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def get_qq_account_pwd(self, index):
        task_name = "获取QQ账号密码"
        log.info(f"{task_name} 开始")
        try:
            for text in self.qq_account_pwd_list:
                if len(text) < 5:
                    continue
                text = text.split("----")
                if int(index) == int(text[2]):
                    return (text[0], text[1])
            return None
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")

    def except_scan(self, index):
        task_name = "异常扫码"
        log.info(f"{task_name} 开始")
        try:
            self.connect(index)
            ld = self.ws.find_element_in_app()
            ld.show()
            sleep(1)
            ld.show()
            rect = ld.bounds()
            rect = (rect.left, rect.top, rect.width(), rect.height())
            sleep(0.5)
            ld.click_center(coords=(0.5, 0.65))
            self.utils.click_image(
                "./src/tool.bmp", find_time=20, region=rect, confidence=0.7)
            self.utils.click_image(
                "./src/scan.bmp", region=rect, confidence=0.4)
            self.utils.find_image_by_template(
                "./src/code.bmp", "all", find_time=30, region=rect, confidence=0.4)
            ld.set_text("{Esc}")
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def pwd_login_new(self, index):
        task_name = "自动登录新"
        log.info(f"{task_name} 开始")
        try:
            self.connect(index)
            ld = self.ws.find_element_in_app()
            ld.show()
            sleep(1)
            ld.show()
            rect = ld.bounds()
            rect = (rect.left, rect.top, rect.width(), rect.height())
            qq_account_pwd = self.get_qq_account_pwd(index)
            if not qq_account_pwd:
                raise Exception("账号密码为空!")
            ld.click_center(coords=(0.2, 0.67))
            ld.set_text("{F2}")
            sleep(0.5)
            ld.set_text("{F2}")
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.35))
            ld.set_text(qq_account_pwd[0])
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.47))
            ld.set_text(qq_account_pwd[1])
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.65))
            self.utils.click_image(
                "./src/tool.bmp", find_time=20, region=rect, confidence=0.7)
            self.utils.click_image(
                "./src/scan.bmp", region=rect, confidence=0.4)
            self.utils.find_image_by_template(
                "./src/code.bmp", "all", find_time=30, region=rect, confidence=0.4)
            ld.set_text("{Esc}")
            sleep(1.5)
            ld.set_text("{F2}")
            sleep(0.5)
            ld.set_text("{F2}")
            sleep(1)
            ld.click_center(coords=(0.2, 0.12))
            sleep(1)
            ld.click_center(coords=(0.2, 0.67))
            sleep(1)
            ld.set_text("{F1}")
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def pwd_login(self, index):
        task_name = "自动输入账号密码登录"
        log.info(f"{task_name} 开始")
        try:
            self.connect(index)
            ld = self.ws.find_element_in_app()
            ld.show()
            sleep(1)
            ld.show()
            rect = ld.bounds()
            rect = (rect.left, rect.top, rect.width(), rect.height())
            qq_account_pwd = self.get_qq_account_pwd(index)
            if not qq_account_pwd:
                raise Exception("账号密码为空!")
            ld.click_center(coords=(0.2, 0.67))
            ld.set_text("{F2}")
            sleep(0.5)
            ld.set_text("{F2}")
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.35))
            ld.set_text(qq_account_pwd[0])
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.47))
            ld.set_text(qq_account_pwd[1])
            sleep(1.5)
            ld.click_center(coords=(0.5, 0.65))
            self.utils.find_image_by_template(
                "./src/tool.bmp", find_time=20, region=rect, confidence=0.7)
            ld.set_text("{F2}")
            sleep(0.5)
            ld.set_text("{F2}")
            sleep(1)
            ld.click_center(coords=(0.2, 0.12))
            sleep(1)
            ld.click_center(coords=(0.2, 0.67))
            sleep(1)
            ld.set_text("{F1}")
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False

    def qq_scan(self, index):
        task_name = "进入QQ扫一扫"
        log.info(f"{task_name} 开始")
        try:
            self.connect(index)
            ld = self.ws.find_element_in_app()
            ld.show()
            sleep(1)
            ld.show()
            rect = ld.bounds()
            rect = (rect.left, rect.top, rect.width(), rect.height())
            log.info(rect)
            self.utils.click_image(
                "./src/tool.bmp", region=rect, confidence=0.7)
            self.utils.click_image(
                "./src/scan.bmp", region=rect, confidence=0.4)
            self.utils.find_image_by_template(
                "./src/code.bmp", "all", find_time=30, region=rect, confidence=0.4)
            self.ld_scan(index)
            if self.utils.find_image_by_template(
                    "./src/login.bmp", region=rect, find_time=3, confidence=0.45):
                self.utils.click_image(
                    "./src/login.bmp", region=rect, confidence=0.45)
            return True
        except Exception as e:
            log.exception(e)
            log.error("{task_name} 出错")
            return False


if __name__ == "__main__":
    print("雷电模拟器 自动化测试")
    ld = LeiDian()
    ld.get_qq_account_pwd_list()
