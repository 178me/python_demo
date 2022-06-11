import sys
from time import sleep
from PyQt5 import (uic, QtGui)
from PyQt5.Qt import (QApplication, QThread, pyqtSignal)
from PyQt5.QtCore import (QObject, Qt)
from PyQt5.QtWidgets import (
    QMainWindow, QHeaderView, QAbstractItemView, QTableWidgetItem,QStyleFactory)
from lib import log, Config, JianGuoYun, Other,CreateDm
from fun_module import ChuanQi


class Console_Stream(QObject):
    console_signal = pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.console_signal.emit(str(text))
        QApplication.processEvents()  # 实时更新UI界面


class MyThread(QThread):
    status_signal = pyqtSignal(str)  # 状态栏消息设置 (考虑后期去掉)

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
                return False
            if self.fun_args:
                result = self.func(self.fun_args)
            else:
                result = self.func()
        except Exception as e:
            print(e)
            if "停止线程" in str(e):
                if self.fun_object:
                    log.info(f"{self.fun_object.index} 号脚本已停止")
            else:
                log.exception(e)
            result = False
        if result:
            if isinstance(result,bool):
                self.status_signal.emit("任务执行成功")
            else:
                self.status_signal.emit(result)
        else:
            if isinstance(result,bool):
                self.status_signal.emit("任务执行失败")
            else:
                self.status_signal.emit(result)


class Function_Run(QObject):
    # 表格状态的信号
    table_signal = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        # 线程对象列表
        self.dll = CreateDm.create_dm()
        self.width,self.height = self.dll.GetScreenWidth(),self.dll.GetScreenHeight()
        self.thread_list = []
        self.list2 = []
        self.qq_info_list = []
        self.one_thread = None

    def start_script(self, args):
        ''' 启动脚本(后期优化成可选择功能) '''
        # 多线程
        for value in args['selected_list']:
            # 获取该模拟器对应的线程对象
            thread = self.search_thread(value["index"])
            if not thread:
                fun_object = ChuanQi()
                thread = MyThread(func=fun_object.main, obj=fun_object,
                                  signal=self.table_signal)
                self.add_thread(thread)
            if thread.isRunning():
                thread.fun_object.thread_status = "运行"
                log.info(f"{value['index']}号脚本运行中")
            else:
                args["script_args"]["index"] = value["index"]
                args["script_args"]["hwnd"] = value["hwnd"]
                thread.fun_args = args["script_args"].copy()
                thread.start()
                sleep(0.5)
        return True

    def stop_script(self, args):
        ''' 停止脚本 '''
        # 多线程
        for value in args['selected_list']:
            # 获取该模拟器对应的线程对象
            thread = self.search_thread(value["index"])
            if not thread:
                continue
            if not thread.isRunning():
                log.info(f"{value['index']}号脚本已停止")
                continue
            thread.fun_object.status = "stop"
            log.info(f"{value['index']}号脚本停止请求发送")
        return True

    def pause_script(self, args):
        ''' 暂停脚本 '''
        # 多线程
        for value in args['selected_list']:
            # 获取该模拟器对应的线程对象
            thread = self.search_thread(value["index"])
            if not thread:
                continue
            if not thread.isRunning():
                log.info(f"{value['index']}号脚本已停止")
                continue
            thread.fun_object.thread_status = "暂停线程"
            log.info(f"{value['index']}号脚本停止请求发送")
        return True

    def stop_thread(self):
        for thread in self.thread_list:
            if not thread.isRunning():
                continue
            thread.fun_object.status = "stop"

    def search_qq_info(self, index):
        ''' 获取模拟器对应的信息 '''
        for qq_info in self.qq_info_list:
            if str(index) in qq_info:
                return qq_info
        return None

    def search_ld(self, index):
        ''' 获取模拟器对应的信息 '''
        for ld_list in self.list2:
            if str(ld_list[0]) != str(index):
                continue
            if str(ld_list[4]) != str(1):
                continue
            return ld_list
        return False

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

    def set_chrome_location(self,args):
        offset_x = 500
        offset_y = 0
        for data in args['selected_list']:
            hwnd = data["hwnd"]
            self.dll.setWindowState(hwnd,1)
            if args["status"] == "隐藏":
                self.dll.MoveWindow(hwnd,self.width - 5,self.height - 30)
            else:
                self.dll.MoveWindow(hwnd,offset_x,offset_y)
                offset_x += 0
                offset_y += 0
        return True

class TableWidget():
    def __init__(self, table):
        # 初始化表格控件
        self.table = table
        # 显示网格
        self.table.setShowGrid(True)
        # 设置表头是否自动排序
        self.table.setSortingEnabled(False)
        # 初始化表格控件
        self.table = table
        # 自动分配
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 指定列可调整列宽
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 50)
        #  self.table.setColumnWidth(2, 300)
        # 选中表头不高亮
        self.table.horizontalHeader().setHighlightSections(False)
        # 隐藏垂直表头
        self.table.verticalHeader().setVisible(False)
        # 取消隔行变色
        self.table.setAlternatingRowColors(False)
        # 不可编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 选中一行
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 多选模式
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setStyleSheet("selection-background-color:#047cd4;")

    def refresh_table(self,dll):
        # 清除表格内容
        self.table.setRowCount(0)
        self.table.clearContents()
        hwnd_list = dll.EnumWindow(0,"360安全浏览器","",1+4).split(",")
        hwnd_list.reverse()
        # 添加表格信息
        for i,value in enumerate(hwnd_list):
            self.table.setRowCount(self.table.rowCount() + 1)
            # ID
            newItem = QTableWidgetItem(str(i))
            # 水平居中 | 垂直居中
            newItem.setTextAlignment(4 | 128)
            self.table.setItem(i, 0, newItem)
            # 句柄
            newItem = QTableWidgetItem(value)
            # 水平居中 | 垂直居中
            newItem.setTextAlignment(4 | 128)
            self.table.setItem(i, 1, newItem)
            # 脚本状态
            newItem = QTableWidgetItem("无")
            newItem.setTextAlignment(4 | 128)
            self.table.setItem(i, 2, newItem)

    def set_item_status(self, index, status_text):
        # 设置脚本状态
        item = self.get_row_by_index(index)
        if item:
            item.setText(status_text)
        QApplication.processEvents()  # 实时更新UI界面

    def get_row_by_index(self, index):
        index = int(index)
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if not item:
                continue
            if int(item.text()) == index:
                return self.table.item(i, 2)
        return None

    def get_selected_list(self):
        ''' 获取已选择的列表 '''
        selected_list = []
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if not item:
                continue
            if not item.isSelected():
                continue
            item2 = self.table.item(i, 1)
            if not item2:
                continue
            if not item2.isSelected():
                continue
            selected_list.append({
                        "index":int(item.text()),
                        "hwnd":int(item2.text())
                        }.copy()
                    )
        return selected_list

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


class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.version = "V1.0.0"
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
        except Exception as e:
            log.exception(e)

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
                if value.isdigit():
                    value = int(value)
            elif "QTextEdit" in ui_object.metaObject().className():
                value = ui_object.toPlainText()
            elif "QComboBox" in ui_object.metaObject().className():
                value = ui_object.currentText()
            else:
                value = None
            ui_object_param[ui_object_id] = value
        return ui_object_param

    def get_ui_object(self, keys=["btn_", "checkbox_", "cmb_", "text_", "input_"]):
        ''' 获取UI对象 '''
        ui_key_list = keys
        ui_object_list = []
        for attr in dir(self.ui):
            for key in ui_key_list:
                # 根据UI对象名获取
                if key in attr:
                    #  print(getattr(self.ui, attr))
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
            elif "QComboBox" in ui_object.metaObject().className():
                self.config.set(
                    "ui_config", ui_object.objectName(), ui_object.currentText())
        self.config.write()

    def init_data(self):
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
            if "QLineEdit" in ui_object.metaObject().className():
                ui_object.setText(value)
            if "QComboBox" in ui_object.metaObject().className():
                ui_object.setCurrentText(value)

    def init_thread(self):
        self.run_thread = MyThread()

    def init_run(self):
        # 获取雷电路径
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

    def init_connect(self):
        ''' 按钮连接 '''
        # 初始化表格
        self.table = TableWidget(self.ui.table_emulator)
        self.table.refresh_table(self.fc_run.dll)
        self.fc_run.table_signal.connect(self.table.set_item_status)
        # 绑定表格变化
        # 状态栏
        self.run_thread.status_signal.connect(self.show_message)
        # 模拟器操作
        self.ui.btn_select_all.clicked.connect(self.table.select_all)
        self.ui.btn_select_cancel.clicked.connect(self.table.select_cancel)
        self.ui.btn_select_invert.clicked.connect(self.table.select_invert)
        self.ui.btn_refresh_table.clicked.connect(
                    lambda: self.table.refresh_table(self.fc_run.dll))
        # 脚本设置
        self.ui.btn_startup_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.start_script,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                    "script_args": self.get_ui_object_value([
                        "input_product_index","cmb_fun_switch","checkbox_cut_enable",
                        "input_search_number","input_search_word_index","input_pay",
                        "input_online_product","input_gdp","input_group_number",
                            ])
                }
            }))
        self.ui.btn_stop_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.stop_script,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                }
            }))
        self.ui.btn_pause_script.clicked.connect(
            lambda: self.task_manage({
                "name": self.fc_run.pause_script,
                "args": {
                    "selected_list": self.table.get_selected_list(),
                }
            }))

    def init_ui(self):
        # 隐藏控制台
        Other.set_console(False)
        # 设置窗口标题
        self.ui.setWindowTitle(f"辅助 {self.version}")
        # 窗口置顶
        self.ui.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.ui.resize(650, 500)
        QApplication.setStyle('Fusion')
        self.table.select_all()
        # 窗口显示
        self.ui.show()

    def closeEvent(self, event):
        ''' 关闭事件 '''
        try:
            self.save_data()
            self.fc_run.stop_thread()
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
        cursor = self.ui.text_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.text_console.setTextCursor(cursor)
        self.ui.text_console.ensureCursorVisible()

    def task_is_run(self):
        ''' 判断线程是否正在运行 '''
        return self.run_thread.isRunning()

    def task_manage(self, task_info):
        ''' 任务管理 '''
        if self.task_is_run():
            self.show_message("已有任务在进行中")
            return False
        self.run_thread.func = task_info["name"]
        if "args" in task_info:
            self.run_thread.fun_args = task_info["args"]
        else:
            self.run_thread.fun_args = None
        self.run_thread.start()

    def show_message(self, text):
        ''' 显示状态栏消息 '''
        self.ui.statusbar.showMessage(text, 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainwindow()
    sys.exit(app.exec_())
