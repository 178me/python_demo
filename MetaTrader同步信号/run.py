from time import sleep
from lib import log
from meta_trader import MetaTraderApp


class Run:
    def __init__(self, index) -> None:
        self.thread_status = "初始化"
        self.params = {}
        self.index = int(index)
        self.set_table_data = None
        self.init_var()

    def init_var(self):
        self.mt = None

    def init_mt(self,path):
        self.mt = MetaTraderApp(path)
        self.mt.pretreatment = self.pretreatment
        self.mt.trading_signals = self.params.get("trading_signals",None)
        self.mt.init_user_list(self.params.get("user_list",""))
        if self.set_table_data:
            self.set_table_data.emit(self.index, {
                "1": str(self.mt.get_account_info()),
            })

    def exit(self):
        self.thread_status = "停止"
        self.set_status("停止")

    def set_status(self, status_text):
        ''' 设置脚本状态 '''
        self.status = status_text
        if self.set_table_data:
            self.set_table_data.emit(self.index, {
                "4": self.thread_status,
            })

    def read_params(self):
        pass

    def pretreatment(self, task_name):
        if "停止" in self.thread_status:
            self.exit()
            self.thread_status = "停止"
            self.set_status(self.status)
            log.info("停止线程")
            raise Exception("停止线程")
        elif "暂停" in self.thread_status:
            self.thread_status = "暂停"
            self.set_status(self.status)
            while "暂停" in self.thread_status:
                sleep(1)
            self.read_params()
        if task_name != "":
            log.info(task_name + " 开始")
            self.set_status(task_name)

    def main(self, params={}):
        self.thread_status = "运行"
        self.params = params
        log.info(params)
        fun_name = self.params.get("fun_name","无")
        self.set_status("")
        if fun_name == "监控":
            self.mt.price = self.params.get("price",0.01)
            if self.mt:
                self.mt.monitor_orders()
            else:
                log.error("该账号未初始化!")
        elif fun_name == "初始化":
            self.init_mt(self.params.get("path",None))
        else:
            log.error("未知功能!")
        self.exit()


if __name__ == "__main__":
    print("主流程测试")
