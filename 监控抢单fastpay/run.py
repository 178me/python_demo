import os
import keyboard
from time import sleep, time
from lib import log, Other
from auto_monitor import Fun1


class Run:
    def __init__(self, index=0) -> None:
        self.thread_status = "初始化"
        self.params = {}
        self.index = int(index)
        self.set_table_data = None
        self.init_object()
        self.init_var()

    def init_object(self):
        self.fun1 = Fun1("Chrome")
        self.fun1.pretreatment = self.pretreatment

    def init_var(self):
        keyboard.add_hotkey('F2', lambda: self.set_thread_status("开始"))
        keyboard.add_hotkey('F3', lambda: self.set_thread_status("暂停"))
        keyboard.add_hotkey('F4', lambda: self.set_thread_status("停止"))

    def exit(self):
        self.thread_status = "停止"
        self.fun1.quit()

    def set_thread_status(self, status_text):
        ''' 设置线程状态 '''
        self.thread_status = status_text
        self.fun1.thread_status = status_text
        log.info(self.thread_status)

    def set_status(self, status_text):
        ''' 设置脚本消息 '''
        self.status = status_text
        if self.set_table_data:
            self.set_table_data.emit(self.index, {
                "3": self.status,
            })

    def read_params(self):
        self.params

    def pretreatment(self, task_name=""):
        if "停止" in self.thread_status:
            self.exit()
            self.thread_status = "停止"
            self.set_status(self.status)
            log.info("停止线程")
            raise Exception("停止线程")
        elif "暂停" in self.thread_status:
            self.thread_status = "暂停"
            self.set_status(self.status)
            self.fun1.beep()
            while "暂停" in self.thread_status:
                sleep(1)
            self.read_params()
        if task_name != "":
            log.info(task_name + " 开始")
            self.set_status(task_name)

    def set_console(self):
        os.system("mode con cols=50 lines=30")

    def main(self, params={}):
        self.thread_status = "运行"
        self.params = params
        #  self.set_console()
        log.info(""" 监控抢单订单 """)
        delay = input("刷新频率(默认 3): ")
        if Other.is_number(delay) == "Nan":
            delay = "3"
        delay = int(delay)
        min_price = input("最低订单金额(默认 50000): ")
        is_result = Other.is_number(min_price)
        if  is_result == "Nan":
            min_price = "50000"
        min_price = float(min_price)
        log.info(f"当前最低价格:{min_price}")
        log.info(f"当前刷新频率:{delay}")
        input("转到今昨订单页后回车继续")
        try:
            start_time = time() + delay
            self.fun1.switch_iframe()
            while True:
                operate_btn_list = self.fun1.get_operate_btn()
                if operate_btn_list:
                    for operate_btn in operate_btn_list:
                        price = self.fun1.get_price(operate_btn["elem"])
                        price = float(price)
                        if price < min_price:
                            log.info(f"价格大于{min_price}")
                            continue
                        self.fun1.click_operate_btn(operate_btn["elem"])
                        self.set_thread_status("暂停")
                        self.pretreatment("")
                        log.info("继续脚本!")
                        break
                for i in range(delay, 1, -1):
                    log.info(f"等待中:{i}")
                    sleep(1)
                if time() > start_time:
                    start_time = time() + delay
                self.fun1.refresh_web()
                os.system("cls")
        except Exception as e:
            if str(e) == "停止线程":
                self.exit()
                exit(0)
            log.exception(e)
            log.error(f"功能执行失败")
        log.info("脚本完成 即将退出!")
        if os.name == "nt":
            os.system("pause")


if __name__ == "__main__":
    log.debug("主流程测试")
    run = Run()
    run.main()
