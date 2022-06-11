try:
    import os
    import sys
    sys.path.append(os.path.join(os.path.split(__file__)[0], "lib_178me"))
except:
    "防止格式化改变顺序"
    import os
import ctypes
from lib_178me.log import log, modify_log_level
from fun.aizhijia import AiZhiJia
modify_log_level(20)

class Run(AiZhiJia):
    def __init__(self) -> None:
        super(Run, self).__init__()


if __name__ == "__main__":
    moudle_name = os.path.split(__file__)[-1]
    log.debug(f"{moudle_name} 测试")
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x00|0x100))
    run = Run()
    run.help()
    run.read_params()
    run.main()
