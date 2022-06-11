import ctypes
import sys
from warnings import simplefilter
from time import time, sleep
import requests
from PyQt5 import (uic, QtGui)
from PyQt5.Qt import (QApplication, QThread, pyqtSignal)
from PyQt5.QtCore import (QObject, Qt)
from PyQt5.QtWidgets import QMainWindow
from XiaoLiZi import XLZ
from LeiDian import LeiDian
from lib import log
from update import JianGuoYun


class Console_Stream(QObject):
    console_signal = pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.console_signal.emit(str(text))
        QApplication.processEvents()


class MyThread(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self):
        super(MyThread, self).__init__()
        self.current_task = None
        self.current_args = None

    def run(self):
        ''' 执行对应的任务 '''
        try:
            if self.current_args:
                result = self.current_task(self.current_args)
            else:
                result = self.current_task()
        except Exception as e:
            log.exception(e)
            result = False
        if result:
            self.status_signal.emit("任务执行成功")
        else:
            self.status_signal.emit("任务执行失败")


class Function_Run():
    def __init__(self):
        global app
        self.xlz = None
        self.ld = None
        self.jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        self.app = app

    def batch_login(self, args):
        ''' 批量登录 '''
        if not self.xlz:
            self.xlz = XLZ(self.app)
            self.xlz.connect()
        if not self.xlz.ws.app:
            return False
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        for i in range(device_encode, len(self.ld.list2)):
            try:
                self.login({"device_encode": i})
                sleep(5)
            except Exception as e:
                log.info(self.ld.list2[i][1] + "登录出错 跳过")
        return True

    def batch_input(self, args):
        ''' 批量登录 '''
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        for i in range(device_encode, len(self.ld.list2)):
            try:
                self.pwd_login({"device_encode": i})
                sleep(3)
            except Exception as e:
                log.info(self.ld.list2[i][1] + "登录出错 跳过")
        return True

    def batch_input_new(self, args):
        ''' 批量登录 '''
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        for i in range(device_encode, len(self.ld.list2)):
            try:
                self.pwd_login_new({"device_encode": i})
                sleep(3)
            except Exception as e:
                log.info(self.ld.list2[i][1] + "登录出错 跳过")
        return True

    def batch_import_qq(self):
        ''' 批量导入QQ '''
        if not self.xlz:
            self.xlz = XLZ(self.app)
            self.xlz.connect()
        if not self.xlz.ws.app:
            return False
        if not self.ld:
            self.ld = LeiDian()
        self.ld.get_ld_status()
        all_qq_text = self.ld.get_all_qq_number()
        return self.xlz.bulk_import_qq(all_qq_text)

    def login_select_qq(self, args):
        ''' 登录选中QQ '''
        if not self.xlz:
            self.xlz = XLZ(self.app)
            self.xlz.connect()
        if not self.xlz.ws.app:
            return False
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        qq_number = self.ld.get_qq_number(device_encode)
        return self.xlz.login_select_qq(qq_number)

    def scan_code(self, args):
        ''' 扫码 '''
        if not self.xlz:
            self.xlz = XLZ(self.app)
            self.xlz.connect()
        if not self.xlz.ws.app:
            return False
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        qq_number = self.ld.get_qq_number(device_encode)
        self.xlz.load_window_screenshot(qq_number)
        return self.ld.qq_scan(device_encode)

    def login(self, args):
        ''' 登录 '''
        if not self.xlz:
            self.xlz = XLZ(self.app)
            self.xlz.connect()
        if not self.xlz.ws.app:
            return False
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        qq_number = self.ld.get_qq_number(device_encode)
        self.xlz.login_select_qq(qq_number)
        self.xlz.load_window_screenshot(qq_number)
        if not self.ld.qq_scan(device_encode):
            self.xlz.load_window_close()
            return False
        return True

    def pwd_login(self, args):
        ''' 登录 '''
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        if not self.ld.qq_account_pwd_list:
            self.ld.get_qq_account_pwd_list()
        self.ld.pwd_login(device_encode)
        return True

    def pwd_login_new(self, args):
        ''' 登录 '''
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        if not self.ld.qq_account_pwd_list:
            self.ld.get_qq_account_pwd_list()
        self.ld.pwd_login_new(device_encode)
        return True

    def except_scan(self, args):
        ''' 登录 '''
        if not self.ld:
            self.ld = LeiDian()
        device_encode = int(args["device_encode"])
        self.ld.connect(device_encode)
        if not self.ld.ws.app:
            return False
        if not self.ld.qq_account_pwd_list:
            self.ld.get_qq_account_pwd_list()
        self.ld.except_scan(device_encode)
        return True

    def run_code(self):
        code = self.jgy.get("python_project/qq_login/code.py").content
        code = code.decode(encoding="utf-8")
        eval(code)


class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # UI
        self.ui = uic.loadUi("./src/mainwindow.ui")
        self.init_stdout()
        self.init_thread()
        self.init_run()
        self.init_event()
        self.init_connect()
        self.init_ui()
        hideConsole()

    def init_thread(self):
        self.run_thread = MyThread()

    def init_run(self):
        self.fc_run = Function_Run()

    def init_event(self):
        self.ui.closeEvent = self.closeEvent

    def init_stdout(self):
        sys.stdout = Console_Stream(console_signal=self.console_output)
        sys.stderr = Console_Stream(console_signal=self.console_output)
        if hasattr(log, "setSteam"):
            log.handlers[1].setStream(sys.stdout)
        else:
            log.handlers[1].stream = sys.stdout

    def init_connect(self):
        ''' 按钮连接 '''
        # 状态栏
        self.run_thread.status_signal.connect(self.show_message)
        # 框架按钮
        self.ui.btn_batch_login_xlz.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.batch_login,
                "args": {
                    "device_encode": self.ui.spin_number_xlz.text()
                }
            }))
        self.ui.btn_login_xlz.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.login,
                "args": {
                    "device_encode": self.ui.spin_number_xlz.text()
                }
            }))
        self.ui.btn_batch_import_qq.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.batch_import_qq
            }))
        self.ui.btn_login_select_qq.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.login_select_qq,
                "args": {
                    "device_encode": self.ui.spin_number_xlz.text()
                }
            }))
        self.ui.btn_scan_code.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.scan_code,
                "args": {
                    "device_encode": self.ui.spin_number_xlz.text()
                }
            }))
        # 上号按钮
        self.ui.btn_batch_login_qq.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.batch_input,
                "args": {
                    "device_encode": self.ui.spin_number_login.text()
                }
            }))
        self.ui.btn_batch_login_qq_new.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.batch_input_new,
                "args": {
                    "device_encode": self.ui.spin_number_login.text()
                }
            }))
        self.ui.btn_pwd_login.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.pwd_login,
                "args": {
                    "device_encode": self.ui.spin_number_login.text()
                }
            }))
        self.ui.btn_pwd_login_new.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.pwd_login_new,
                "args": {
                    "device_encode": self.ui.spin_number_login.text()
                }
            }))
        self.ui.btn_except_scan.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.except_scan,
                "args": {
                    "device_encode": self.ui.spin_number_login.text()
                }
            }))
        # 控制台按钮
        self.ui.btn_run_code.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.run_code
            }))

    def init_ui(self):
        self.button_list = [
            self.ui.btn_batch_login_xlz, self.ui.btn_login_xlz, self.ui.btn_batch_import_qq,
            self.ui.btn_login_select_qq, self.ui.btn_scan_code,
            self.ui.btn_batch_login_qq, self.ui.btn_pwd_login,
            self.ui.btn_batch_login_qq_new, self.ui.btn_pwd_login_new,
            self.ui.btn_run_code,
        ]
        desktop = QApplication.desktop()
        self.ui.move(int(desktop.width()*0.85), int(desktop.height()*0.45))
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ui.show()

    def closeEvent(self, event):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        if hasattr(log, "setSteam"):
            log.handlers[1].setStream(sys.stdout)
        else:
            log.handlers[1].stream = sys.stdout

    def console_output(self, text):
        """ 输出日志到控制台 """
        cursor = self.ui.text_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.text_console.setTextCursor(cursor)
        self.ui.text_console.ensureCursorVisible()

    def task_is_run(self):
        ''' 判断是否正在运行 '''
        return self.run_thread.isRunning()

    def task_manage(self, task_info):
        ''' 任务管理 '''
        if self.task_is_run():
            self.show_message("已有任务在进行中")
            return False
        self.run_thread.current_task = task_info["name"]
        if "args" in task_info:
            self.run_thread.current_args = task_info["args"]
        else:
            self.run_thread.current_args = None
        self.run_thread.start()

    def set_all_button(self, status=True):
        ''' 设置所有按钮 '''
        for btn in self.button_list:
            btn.setEnabled(status)

    def show_message(self, text):
        ''' 显示状态栏消息 '''
        if "任务执行" in text:
            self.set_all_button(True)
        else:
            self.set_all_button(False)
        self.ui.statusbar.showMessage(text)

    def test(self):
        ''' 测试功能 '''
        pass


def get_netpad_text(note_id=""):
    ''' 获取网络剪贴板的内容,需要json request warnings库
    :param note_id: 剪贴板id
    :return: data || error
    '''
    # 如果标题为空的话获取所有标题
    netpad_url = "https://netcut.cn/api/note/data/?note_id=" + \
        note_id + "&_=" + str(int(time()))
    # 获取所有该用户名所有文本 verify是否忽略安全证书 我这里不忽略会报错
    simplefilter("ignore")
    result = requests.post(
        netpad_url,
        verify=False,
    ).json()
    if result["error"] == "":
        del result["data"]["log_list"]
        return result["data"]
    return result['error']


def hideConsole():
    """
    Hides the console window in GUI mode. Necessary for frozen application, because
    this application support both, command line processing AND GUI mode and theirfor
    cannot be run via pythonw.exe.
    """
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)


def showConsole():
    """Unhides console window"""
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 1)


if __name__ == "__main__":
    #  vertivity = get_netpad_text("635086388d0288f1")["note_content"]
    #  if vertivity.strip() != "1":
    #  exit(0)
    app = QApplication(sys.argv)
    window = mainwindow()
    sys.exit(app.exec_())
