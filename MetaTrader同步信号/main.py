import json
import os
import sys
import datetime
import time
import psutil
from time import sleep
from PyQt5 import (uic, QtGui)
from PyQt5.Qt import (QApplication, QThread, pyqtSignal)
from PyQt5.QtCore import (QObject, Qt)
from PyQt5.QtWidgets import (
    QMainWindow, QHeaderView, QAbstractItemView, QTableWidgetItem)
from lib import log, Config, JianGuoYun, Other
from run import Run


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
            self.fun_object.set_table_data = signal

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
            if "停止线程" == str(e):
                if self.fun_object:
                    log.info(f"{self.fun_object.index}号脚本被你终止啦")
            else:
                log.exception(e)
            result = False
            #  if result:
            #  log.info("完美结束啦!")
            #  else:
            #  log.warning("失败了哦")


class Function_Run(QObject):
    # 表格状态的信号
    table_signal = pyqtSignal(int, dict)
    # 交易信号
    trading_signals = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        self.jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        # 线程对象列表
        self.thread_list = []

    def start_script(self, args):
        ''' 启动脚本(后期优化成可选择功能) '''
        for item in args['selected_list']:
            # 获取该模拟器对应的线程对象
            index = int(item[0])
            thread = self.search_thread(index)
            if not thread:
                fun_object = Run(index)
                thread = MyThread(func=fun_object.main, obj=fun_object,
                                  signal=self.table_signal)
                self.add_thread(thread)
            args["script_args"]["path"] = item[2]
            args["script_args"]["user_list"] = item[3]
            if thread.isRunning():
                if thread.fun_object.thread_status == "运行":
                    thread.fun_object.thread_status = "运行"
                    log.info(f"脚本已经在运行了")
                else:
                    thread.fun_object.thread_status = "运行"
                    thread.fun_object.params = args["script_args"].copy()
            else:
                thread.fun_args = args["script_args"].copy()
                thread.start()
                sleep(0.1)
        return True

    def set_thread_statu(self, args):
        ''' 设置脚本状态 '''
        status = args["status"]
        for item in args['selected_list']:
            index = int(item[0])
            thread = self.search_thread(index)
            if not thread:
                continue
            if not thread.isRunning():
                log.warning(f"脚本没有运行哦")
                thread.fun_object.thread_status = "停止"
                continue
            if status in "运行":
                thread.fun_object.params = args["script_args"].copy()
            thread.fun_object.thread_status = status
            log.info(f"{status}请求发送成功啦")
        return True

    def stop_all_thread(self):
        ''' 获取线程对象 '''
        for thread in self.thread_list:
            if not thread.fun_object:
                continue
            thread.fun_object.thread_status = "停止"

    def search_thread(self, index):
        ''' 获取线程对象 '''
        for thread in self.thread_list:
            if not thread.fun_object:
                continue
            if thread.fun_object.index != index:
                continue
            return thread
        return False

    def add_thread(self, thread):
        ''' 添加线程对象 '''
        self.thread_list.append(thread)


class TableWidget():
    def __init__(self, table):
        self.fc_run = None
        # 初始化表格控件
        self.table = table
        # 显示网格
        self.table.setShowGrid(True)
        # 设置表头是否自动排序
        self.table.setSortingEnabled(False)
        # 自动分配列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 内容自适应
        self.table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        # 调整列宽
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 25)
        self.table.setColumnWidth(3, 250)
        # 选中表头不高亮
        self.table.horizontalHeader().setHighlightSections(False)
        # 取消隔行变色
        self.table.setAlternatingRowColors(False)
        # 隐藏垂直表头
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        # 不可编辑
        #  self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 选中一行
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 多选模式
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        # 设置选中颜色
        self.table.setStyleSheet("selection-background-color:#047cd4;")

    def select_all(self):
        ''' 选择全部 '''
        self.table.selectAll()
        return True

    def select_cancel(self):
        ''' 取消选择 '''
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if not item:
                    continue
                item.setSelected(False)

    def select_invert(self):
        ''' 反向选择 '''
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if not item:
                    continue
                if item.isSelected():
                    item.setSelected(False)
                else:
                    item.setSelected(True)

    def get_table_data(self) -> list:
        table_data = []
        for index, list_name in enumerate(os.listdir("./MetaTraderApp")):
            table_data.append([index+1, "", list_name, "", "未开始"])
        return table_data

    def init_table(self):
        """ 初始化表格 """
        # 清除表格内容
        self.table.setRowCount(0)
        self.table.clearContents()
        table_data = self.get_table_data()
        for row, data in enumerate(table_data):
            self.table.setRowCount(self.table.rowCount() + 1)
            for column, value in enumerate(data):
                newItem = QTableWidgetItem(str(value))
                # 水平居中 | 垂直居中
                newItem.setTextAlignment(4 | 128)
                self.table.setItem(row, column, newItem)

    def refresh_table_data(self):
        """ 刷新表格数据 """
        pass

    def set_table_data(self, index: int, table_data={}):
        """ 设置表格数据 """
        for column, data in table_data.items():
            column = int(column)
            row = self.get_row_by_index(index)
            if row == None:
                log.warning("更新数据失败啦,木有找到对应的编号")
                break
            self.table.item(row, column).setText(data)
        self.table.viewport().update()

    def get_row_by_index(self, index):
        """ 获取指定表格项 """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if not item:
                continue
            if item.text() == str(index):
                return row
        return None

    def get_selected_list(self):
        ''' 获取已选择的列表 '''
        selected_list = []
        for i in range(self.table.rowCount()):
            temp_list = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if not item:
                    temp_list.append(None)
                    continue
                if not item.isSelected():
                    temp_list = []
                    break
                temp_list.append(item.text())
            if temp_list:
                selected_list.append(temp_list)
        return selected_list

    def set_sync_list(self, list1):
        ''' 获取同步列表 '''
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 3)
            if not item:
                continue
            if len(list1) == i:
                continue
            item.setText(list1[i])

    def get_sync_list(self):
        ''' 获取同步列表 '''
        list1 = []
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 3)
            if not item:
                continue
            list1.append(item.text())
        return list1

    def get_user_list(self,user_list):
        ''' 获取已选择的列表 '''
        selected_list = []
        for i in range(self.table.rowCount()):
            temp_list = []
            for j in range(self.table.columnCount()):
                if self.table.item(i, 0).text() not in user_list:
                    break
                item = self.table.item(i, j)
                if not item:
                    temp_list.append(None)
                    continue
                temp_list.append(item.text())
            if temp_list:
                selected_list.append(temp_list)
        print(selected_list)
        return selected_list


class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "V1.0.0"
        self.password_verfity()
        # 加载UI
        try:
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
        except Exception as e:
            self.closeEvent(1)
            log.exception(e)
            #  input("加载窗口出错了~回车退出:")

    def password_verfity(self):
        #  password = input("请输入密码:")
        my_password = None
        try:
            my_password = Other.get_netpad_text("49f7bf33400964f6")["note_content"].replace("\n","")
        except:
            log.info("遇到错误~")
        if "123" != my_password:
            sys.exit(0)

    def init_run(self):
        # 功能模块
        self.fc_run = Function_Run()

    def init_event(self):
        # 关闭事件
        self.ui.closeEvent = self.closeEvent

    def init_stdout(self):
        sys.stdout = Console_Stream(console_signal=self.console_output)
        sys.stderr = Console_Stream(console_signal=self.console_output)
        if hasattr(log, "setSteam"):
            log.handlers[1].setStream(sys.stdout)
        else:
            log.handlers[1].stream = sys.stdout

    def get_ui_object(self, ui_key_list=["checkbox_", "cmb_", "input_"]):
        ''' 获取UI对象 '''
        ui_key_list = ["checkbox_", "cmb_", "input_","spinbox_"]
        ui_object_list = []
        for attr in dir(self.ui):
            for key in ui_key_list:
                # 根据UI对象名获取
                if key in attr:
                    ui_object_list.append(getattr(self.ui, attr))
        return ui_object_list

    def restore_data(self):
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
            elif "QDoubleSpinBox" in ui_object.metaObject().className():
                ui_object.setValue(float(value))
        sync_list = self.config.get("table_data", "sync_list")
        if sync_list:
            sync_list = json.loads(sync_list)
            self.table.set_sync_list(sync_list)

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
            elif "QDoubleSpinBox" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), str(ui_object.value()))
        self.config.set("table_data", "sync_list",
                        json.dumps(self.table.get_sync_list()))
        self.config.write()

    def get_ui_object_value(self, id_list=[]):
        ''' 获取UI对象的值 '''
        ui_object_param = {}
        for ui_object in id_list:
            if "QCheckBox" in ui_object.metaObject().className():
                value = ui_object.isChecked()
            elif "QLineEdit" in ui_object.metaObject().className():
                value = ui_object.text()
                if Other.is_number(value) == "int":
                    value = int(value)
                elif Other.is_number(value) == "float":
                    value = round(float(value))
            elif "QTextEdit" in ui_object.metaObject().className():
                value = ui_object.toPlainText()
            elif "QComboBox" in ui_object.metaObject().className():
                value = ui_object.currentText()
            elif "QDoubleSpinBox" in ui_object.metaObject().className():
                value = ui_object.value()
            else:
                value = None
            ui_object_id = str(ui_object.objectName())
            ui_object_param[ui_object_id] = value
        return ui_object_param

    def closeEvent(self, event):
        ''' 关闭事件 '''
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            if hasattr(log, "setSteam"):
                log.handlers[1].setStream(sys.stdout)
            else:
                log.handlers[1].stream = sys.stdout
            self.save_data()
            self.run_time = None
            self.fc_run.stop_all_thread()
        except Exception as e:
            log.exception(e)

    def console_output(self, text):
        """ 输出日志到控制台 """
        cursor = self.ui.text_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        text = text.replace("[31m", "")
        text = text.replace("[32m", "")
        text = text.replace("[33m", "")
        text = text.replace("[0m", "")
        cursor.insertText(text)
        if cursor.position() > self.max_buffer_size:
            self.ui.text_console.clear()
        self.ui.text_console.setTextCursor(cursor)
        self.ui.text_console.ensureCursorVisible()

    def show_info(self):
        while self.run_time != None:
            s = (datetime.datetime.now() - self.run_time).seconds
            local = time.localtime(3600 * 16 + s)
            run_time = time.strftime("%H:%M:%S", local)
            self.ui.lab_run_time.setText(f"运行时间: {run_time}")
            self.ui.lab_mem.setText(f"内存: {psutil.virtual_memory().percent}%")
            self.ui.lab_cpu.setText(f"CPU: {psutil.cpu_percent(None)}%")
            sleep(1)

    def task_is_run(self):
        ''' 判断线程是否正在运行 '''
        return self.run_thread.isRunning()

    def task_manage(self, task_info):
        ''' 任务管理 '''
        if self.task_is_run():
            print("没有")
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

    def init_data(self):
        # 初始化配置模块
        self.config = Config()
        # 获取所有UI对象
        self.ui_object_list = self.get_ui_object()
        # 运行时间
        self.run_time = datetime.datetime.now()
        self.max_buffer_size = 1024 * 128

    def init_thread(self):
        # UI执行线程
        self.run_thread = MyThread()
        # 状态栏线程
        self.time_thread = MyThread()
        self.time_thread.func = self.show_info
        self.time_thread.start()

    def init_connect(self):
        ''' 按钮连接 '''
        # 初始化表格
        self.table = TableWidget(self.ui.table_script)
        self.table.init_table()
        # 表格数据槽函数连接
        self.fc_run.table_signal.connect(self.table.set_table_data)
        self.fc_run.trading_signals.connect(self.trading)
        # 表格操作
        self.ui.btn_select_all.clicked.connect(self.table.select_all)
        self.ui.btn_select_cancel.clicked.connect(self.table.select_cancel)
        self.ui.btn_select_invert.clicked.connect(self.table.select_invert)
        self.ui.btn_refresh_table.clicked.connect(
            self.table.refresh_table_data)
        # 脚本设置
        self.ui.btn_startup_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.start_script,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                    "script_args": {
                        "fun_name": "监控",
                        "price": self.ui.spinbox_price.value()
                    }
                }
            }))
        self.ui.btn_stop_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.set_thread_statu,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                    "status": "停止"
                }
            }))
        self.ui.btn_pause_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.set_thread_statu,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                    "status": "暂停"
                }
            }))
        self.ui.btn_init_client.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.start_script,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                    "script_args": {
                        "fun_name": "初始化",
                    }
                }
            }))

    def init_ui(self):
        # 隐藏控制台
        Other.set_console(False)
        # 窗口置顶
        self.table.select_all()
        self.restore_data()
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 设置窗口图标
        self.ui.setWindowIcon(QtGui.QIcon("./input/logo.ico"))
        # 设置窗口标题
        self.ui.setWindowTitle(f"辅助 {self.version}")
        # 窗口大小设置
        self.ui.resize(750, 550)
        desktop = QApplication.desktop()
        self.ui.move(int(desktop.width()*0.60), int(desktop.height()*0.40))
        QApplication.setStyle('Fusion')
        # 窗口显示
        self.ui.show()

    def trading(self, user_list, positions):
        self.fc_run.start_script({
                "selected_list": self.table.get_user_list(user_list),
                "script_args": {
                    "fun_name": "交易",
                    "positions":positions
                }
            })


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainwindow()
    sys.exit(app.exec_())
