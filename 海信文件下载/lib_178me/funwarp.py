""" 功能函数装饰器

例子:
@FunWrap("功能描述",True)
def test():
    pass

"""
from time import time
from functools import wraps
from log import log

class FunWrap(object):
    def __init__(self, fun_name="", is_raise=False,computer_run_time=False):
        # 功能标识名
        self.fun_name = fun_name
        # 是否抛出异常
        self.is_raise = is_raise
        self.computer_run_time = computer_run_time

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                # 预处理 args[0] 一般是类对象self 所以该方法用于类
                if len(args) != 0:
                    if hasattr(args[0], "pretreatment"):
                        args[0].pretreatment()
                if self.fun_name != "":
                    log.debug(self.fun_name + " 开始")
                if self.computer_run_time:
                    start_time = time()
                    result = func(*args, **kwargs)
                    end_time = time()
                    log.debug(f"{self.fun_name} 运行时间:{end_time - start_time} 秒")
                else:
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                if "停止线程" in str(e) or self.is_raise:
                    raise e
                else:
                    log.exception(e)
                    log.error(f"{self.fun_name} 功能发生异常")
                    return False
        return wrapped_function
