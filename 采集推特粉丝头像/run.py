import os
import ctypes
from lib_178me.log import log, modify_log_level
from fun.fun1 import Fun1
from time import sleep
modify_log_level(20)

class Run(Fun1):
    def __init__(self) -> None:
        super(Run,self).__init__(root_path=".")
        self.thread_status = "初始化"

    def exit(self):
        ''' 退出需要做的一些操作 '''
        self.thread_status = "停止"

    def set_thread_status(self, status_text):
        ''' 设置线程状态 '''
        self.thread_status = status_text
        log.info(f"线程状态:{self.thread_status}")

    def read_params(self, params):
        ''' 对读取的参数进行处理 '''
        self.params = params.copy()

    def pretreatment(self):
        ''' 功能函数预处理 '''
        if "停止" in self.thread_status:
            self.exit()
            self.thread_status = "停止"
            log.info("停止线程")
            raise Exception("停止线程")
        elif "暂停" in self.thread_status:
            self.thread_status = "暂停"
            while "暂停" in self.thread_status:
                sleep(1)

if __name__ == "__main__":
    if os.name == "nt":
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x00|0x100))
    run = Run()
    if os.name == "nt":
        import keyboard
        keyboard.add_hotkey('F2', lambda: run.set_thread_status("开始"))
        keyboard.add_hotkey('F3', lambda: run.set_thread_status("暂停"))
        keyboard.add_hotkey('F4', lambda: run.set_thread_status("停止"))
    while True:
        try:
            run.main()
        except Exception as e:
            log.exception(e)
            input("出现错误")
        if os.name == "nt":
            os.system("cls")
