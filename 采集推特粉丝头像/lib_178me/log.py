""" 日志
"""
import os
import logging
from colorlog import ColoredFormatter
from concurrent_log_handler import ConcurrentRotatingFileHandler
LOG_COLOR = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
LOG_PATH = "./log"


def modify_log_level(level=10):
    """ 修改日志等级
        CRITICAL = 50
        ERROR = 40
        WARNING = 30
        INFO = 20
        DEBUG = 10
    """
    log.handlers[1].setLevel(level)


def modify_format(run_mode="console"):
    if run_mode == "console":
        formatter = ColoredFormatter(
            fmt='%(log_color)s%(asctime)s.%(msecs)03d:%(levelname)s \n`-> %(message)s',
            log_colors=LOG_COLOR
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d:%(levelname)s \n`-> %(message)s')
    formatter.datefmt = "%H:%M:%S"
    log.handlers[1].setFormatter(formatter)


log = logging.getLogger('日志')
if len(log.handlers) == 0:
    log.setLevel(level=logging.DEBUG)
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    file_format = logging.Formatter(
        '%(asctime)s.%(msecs)03d:%(levelname)s \n`-> %(message)s')
    file_format.datefmt = "%m-%d %H:%M:%S"
    file_handler = ConcurrentRotatingFileHandler(
        f"{LOG_PATH}/日志.txt", maxBytes=3 * 1024 * 1024, backupCount=10)
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(file_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    modify_format("console")

if __name__ == "__main__":
    moudle_name = os.path.split(__file__)[-1]
    log.debug(f"{moudle_name} 测试")
    log. debug("调试")
    log.info("提示")
    log.warning("警告")
    log.error("错误")
