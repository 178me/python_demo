import sys
from time import sleep
from PyQt5 import (uic, QtGui)
from PyQt5.Qt import (QApplication, QThread, pyqtSignal)
from PyQt5.QtCore import (QObject, Qt)
from PyQt5.QtWidgets import (
    QMainWindow)
from lib import log, Config, JianGuoYun, Other
#  from my_qt_material import apply_stylesheet


class Console_Stream(QObject):
    console_signal = pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.console_signal.emit(str(text))
        QApplication.processEvents()  # 实时更新UI界面


class MyThread(QThread):
    def __init__(self, func=None, args=None, obj=None, signal=None):
        super(MyThread, self).__init__()
        # 要执行的函数
        self.func = func
        # 函数参数
        self.fun_args = args
        # 函数对应的对象
        self.fun_object = obj
        # 给对象设置信号
        if self.fun_object:
            self.fun_object.set_script_message = signal

    def run(self):
        ''' 执行对应的任务 '''
        try:
            if not self.func:
                raise Exception("没有功能被执行")
            if self.fun_args:
                result = self.func(self.fun_args)
            else:
                result = self.func()
        except Exception as e:
            if "停止线程" in str(e):
                if self.fun_object:
                    log.info(f"{self.fun_object.index}号模拟器脚本已停止")
            else:
                log.exception(e)
            result = False


class Function_Run(QObject):

    def __init__(self):
        super().__init__()
        self.jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        # 线程对象列表
        self.thread_list = []
        self.list2 = []
        self.main_thread = None

    def start_script(self, args):
        log.info("启动脚本")
        ''' 启动脚本(后期优化成可选择功能) '''
        if self.main_thread and self.main_thread.fun_object.thread_status == "运行":
            log.info("脚本运行中")
            return True
        elif self.main_thread and self.main_thread.fun_object.thread_status == "暂停":
            self.main_thread.fun_object.thread_status = "运行"
            log.info("脚本恢复运行")
            return True
        elif not self.main_thread:
            from fun_module import VncAuto
            fun_object = VncAuto()
            self.main_thread = MyThread(func=fun_object.main, obj=fun_object)
        self.main_thread.fun_args = args["script_args"]
        self.main_thread.start()
        sleep(0.1)

    def set_thread_status(self, args):
        ''' 设置脚本状态 '''
        status = args["status"]
        if self.main_thread and self.main_thread.isRunning():
            if self.main_thread.fun_object:
                self.main_thread.fun_object.thread_status = status
                log.info(f"{status}请求发送")
            return True

    def stop_thread(self):
        if self.main_thread:
            self.main_thread.quit()

class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 加载UI
        self.ui = uic.loadUi("./input/mainwindow.ui")
        # 初始化控制台输出流
        self.init_stdout()
        # 初始化数据
        self.init_data()
        # 初始化功能函数
        self.init_run()
        # 初始化线程
        self.init_thread()
        # 初始化UI事件
        self.init_event()
        # 初始化连接
        self.init_connect()
        # 初始化UI
        self.init_ui()

    def get_ui_object_value(self, id_list=[]):
        ''' 获取UI对象的值 '''
        ui_object_param = {}
        for ui_object_id in id_list:
            ui_object = getattr(self.ui, ui_object_id, False)
            if not ui_object:
                continue
            if "QCheckBox" in ui_object.metaObject().className():
                value = ui_object.isChecked()
            elif "QLineEdit" in ui_object.metaObject().className():
                value = ui_object.text()
                if Other.is_number(value) == "int":
                    value = int(value)
                elif Other.is_number(value) == "float":
                    value = float(value)
            elif "QTextEdit" in ui_object.metaObject().className():
                value = ui_object.toPlainText()
            elif "QComboBox" in ui_object.metaObject().className():
                value = ui_object.currentText()
            else:
                value = None
            ui_object_param[ui_object_id] = value
        return ui_object_param

    def get_ui_object(self):
        ''' 获取UI对象 '''
        ui_key_list = ["btn_", "checkbox_", "cmb", "text_", "table_", "input_"]
        ui_object_list = []
        for attr in dir(self.ui):
            for key in ui_key_list:
                # 根据UI对象名获取
                if key in attr:
                    # print(attr)
                    ui_object_list.append(getattr(self.ui, attr))
        #  print(ui_object_list)
        return ui_object_list

    def save_data(self):
        for ui_object in self.ui_object_list:
            if "QCheckBox" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), str(ui_object.isChecked()))
            elif "QLineEdit" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), str(ui_object.text()))
            elif "QTextEdit" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), str(ui_object.toPlainText()))
            elif "QComboBox" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), ui_object.currentText())
        self.config.write()

    def init_data(self):
        # 控制变量
        self.pos_enable = False
        self.finish_status = False
        # 初始化配置模块
        self.config = Config()
        # 获取所有UI对象
        self.ui_object_list = self.get_ui_object()
        # 获取UI配置
        ui_config = self.config.get("ui_config")
        # 恢复数据
        for key, value in ui_config:
            ui_object = getattr(self.ui, key, False)
            if not ui_object:
                continue
            if "QCheckBox" in ui_object.metaObject().className():
                if "False" in value:
                    value = False
                else:
                    value = True
                ui_object.setChecked(value)
            elif "QLineEdit" in ui_object.metaObject().className():
                ui_object.setText(value)
            elif "QTextEdit" in ui_object.metaObject().className():
                ui_object.setText(value)
            elif "QComboBox" in ui_object.metaObject().className():
                ui_object.setCurrentText(value)

    def init_thread(self):
        # UI功能线程
        self.run_thread = MyThread()
        # 坐标线程
        self.pos_thread = MyThread()

    def init_run(self):
        # 功能模块
        self.fc_run = Function_Run()

    def init_event(self):
        # 关闭事件
        self.ui.closeEvent = self.closeEvent
        self.ui.showEvent = self.showEvent

    def init_stdout(self):
        sys.stdout = Console_Stream(console_signal=self.console_output)
        sys.stderr = Console_Stream(console_signal=self.console_output)
        if hasattr(log, "setSteam"):
            log.handlers[1].setStream(sys.stdout)
        else:
            log.handlers[1].stream = sys.stdout

    def init_connect(self):
        ''' 按钮连接 '''
        # 模拟器操作
        self.ui.btn_start_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.start_script,
                "args": {
                    "script_args": {
                        "test":"1"
                        }
                }
            }))
        self.ui.btn_pause_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.set_thread_status,
                "args": {
                    "status":"暂停"
                }
            }))
        self.ui.btn_stop_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.set_thread_status,
                "args": {
                    "status":"停止"
                }
            }))
        self.ui.btn_pos_enable.clicked.connect(
            lambda: self.task_manage({
                "name": self.switch_pos_enable
            }))
        self.ui.btn_exit.clicked.connect(self.quit)

    def init_ui(self):
        self.pos_thread.func = self.show_position
        self.pos_thread.start()
        # 窗口置顶
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 窗口置顶
        self.ui.setWindowIcon(QtGui.QIcon("./input/logo.ico"))
        # 窗口显示
        self.ui.show()

    def quit(self):
        app = QApplication.instance()
        app.quit()

    def closeEvent(self, event):
        ''' 关闭事件 '''
        try:
            self.save_data()
            self.fc_run.stop_thread()
            self.finish_status = True
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            if hasattr(log, "setSteam"):
                log.handlers[1].setStream(sys.stdout)
            else:
                log.handlers[1].stream = sys.stdout
        except Exception as e:
            log.exception(e)

    def console_output(self, text):
        """ 输出日志到控制台 """
        cursor = self.ui.browser_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.browser_console.setTextCursor(cursor)
        self.ui.browser_console.ensureCursorVisible()

    def task_is_run(self):
        ''' 判断线程是否正在运行 '''
        return self.run_thread.isRunning()

    def task_manage(self, task_info):
        ''' 任务管理 '''
        if self.task_is_run():
            return False
        self.run_thread.func = task_info["name"]
        if "args" in task_info:
            self.run_thread.fun_args = task_info["args"]
        else:
            self.run_thread.fun_args = None
        self.run_thread.start()

    def show_message(self, text):
        ''' 显示状态栏消息 '''
        self.ui.statusbar.showMessage(text)

    def switch_pos_enable(self):
        self.pos_enable = not self.pos_enable

    def show_position(self):
        from pyautogui import position
        while not self.finish_status:
            if not self.pos_enable:
                sleep(0.1)
                continue
            pos = position()
            self.ui.lab_pos.setText(f"X:{pos.x}    Y:{pos.y}")
            sleep(0.1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #  import os
    #  apply_stylesheet(app, theme='.xml',
    #  path=os.getcwd()+os.sep+"main.py")
    window = mainwindow()
    sys.exit(app.exec_())
