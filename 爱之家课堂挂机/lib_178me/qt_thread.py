import logging
log = logging.getLogger('日志')
from PyQt5.Qt import QThread


class MyThread(QThread):
    def __init__(self, func, args=None, obj=None):
        """ 初始化线程对象
        func: 需要执行的函数
        args: 需要执行的参数
        obj: 绑定对象
        """
        super(MyThread, self).__init__()
        # 要执行的函数
        self.func = func
        # 函数参数
        self.args = args
        # 函数返回值
        self.result = None
        # 绑定对象
        self.obj = obj
        if self.obj:
            self.obj.thread_statu = "初始化"
            self.obj.params = self.args

    def run(self):
        ''' 执行对应的任务 '''
        try:
            if self.obj:
                self.obj.thread_status = "运行"
            if self.args:
                self.result = self.func(self.args)
            else:
                self.result = self.func()
        except Exception as e:
            if str(e) == "停止线程":
                if self.obj:
                    log.info(f"{self.obj.index}号脚本被你终止啦")
                else:
                    log.info(f"脚本被你终止啦")
            else:
                log.exception(e)
            self.result = False
        if self.obj:
            self.obj.thread_status = "停止"
