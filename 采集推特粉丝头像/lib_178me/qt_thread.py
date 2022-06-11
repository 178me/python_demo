from time import time, sleep
from PyQt5.Qt import QThread
import logging
log = logging.getLogger('日志')

class MyThread(QThread):
    def __init__(self, func, args=None, obj=None):
        """ 初始化线程对象
        func: 需要执行的函数
        args: 需要执行的参数
        obj: 绑定对象
        """
        super(MyThread, self).__init__()
        # 绑定对象
        self.obj = obj
        # 要执行的函数
        self.func = getattr(self.obj,func) if isinstance(func,str) else func
        # 函数参数
        self.args = args
        # 函数返回值
        self.result = None
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


class MyThreadPool():
    def __init__(self, thread_count,func="main",args=None,thread_obj=None):
        """ 初始化线程池 """
        self.thread_list = [MyThread(func,args=args,obj=thread_obj() if thread_obj else None) for _ in range(thread_count)]

    def is_free(self):
        for thread in self.thread_list:
            # 判断是否运行
            if thread.isRunning():
                continue
            return True
        return False

    def submit(self, func=None, args=None):
        """ 提交任务
        启动一个空闲线程并返回该线程
        :return 线程对象 | 空
        """
        for thread in self.thread_list:
            # 判断是否运行
            if thread.isRunning():
                continue
            # 修改线程对象的函数和参数，然后启动
            if func:
                thread.func = getattr(thread.obj,func) if isinstance(func,str) else func
            if args:
                thread.args = args
            thread.start()
            return thread
        return None

    def done(self, done_count=1, wait_time=60, interval=0.1):
        """ 等待完成
        等待线程执行完成
        :done_count 完成数量
        :return 线程列表
        """
        assert done_count <= len(self.thread_list),"超出线程列表数量"
        done_count = done_count if done_count > 0 else len(self.thread_list)
        done_list = []
        timeout = time() + wait_time
        while timeout > time():
            for thread in self.thread_list:
                # 跳过已存在的线程
                if thread in done_list:
                    continue
                # 判断结果是否为空
                if thread.isRunning():
                    continue
                done_list.append(thread)
            # 是否等待完成
            if len(done_list) >= done_count:
                break
            sleep(interval)
        return done_list
