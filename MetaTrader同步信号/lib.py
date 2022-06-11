'''
@author: 178me
@description: window自动化操作
'''
try:
    import ctypes
    import re
    import base64
    import requests
    import sys
    import os
    import warnings
    sys.coinit_flags = 2
    warnings.simplefilter("ignore", UserWarning)
except Exception as e:
    pass
import logging
import configparser
import os
from functools import wraps
from time import time
from concurrent_log_handler import ConcurrentRotatingFileHandler
from subprocess import Popen,check_output

run_mode = "界面"
log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}
log = logging.getLogger('日志')
log.setLevel(level=logging.INFO)
if run_mode == "无界面":
    import colorlog
    formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s.%(msecs)03d:%(levelname)s \n`-> %(message)s',
        log_colors=log_colors_config
    )
else:
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d:%(levelname)s \n`-> %(message)s')
formatter.datefmt = "%H:%M:%S"
if not os.path.exists("./out"):
    os.mkdir("out")
file_handler = ConcurrentRotatingFileHandler(
    "./out/日志.txt", maxBytes=3 * 1024 * 1024, backupCount=40)
file_handler.setLevel(level=logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(stream_handler)

# 功能函数模块
class FunWrap(object):
    def __init__(self, task_name="", is_raise=False):
        # 功能标识名
        self.task_name = task_name
        # 是否抛出异常
        self.is_raise = is_raise

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                # 预处理 args[0] 一般是类对象self 所以该方法用于类
                args[0].pretreatment(self.task_name)
                return func(*args, **kwargs)
            except Exception as e:
                if str(e) == "停止线程":
                    raise Exception("停止线程")
                log.exception(e)
                if self.is_raise:
                    raise Exception(f"{self.task_name} 出错")
                else:
                    log.error(f"{self.task_name} 出错")
                    return False
        return wrapped_function


class Config():
    """ 配置文件模块 """

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.getcwd() + os.sep + "input" + os.sep + "config.ini"
        if not os.path.exists(self.config_path):
            file = open(self.config_path, 'w')
            file.close()
        self.config.read(self.config_path, encoding="utf-8")

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get(self, section=None, key=None):
        if key:
            if not self.config.has_option(section, key):
                return None
            return self.config.get(section, key)
        if section:
            if not self.config.has_section(section):
                return []
            return self.config.items(section)
        return self.config.sections()

    def remove(self, section, key=None):
        if not self.config.has_section(section):
            return None
        if key:
            return self.config.remove_option(section, key)
        return self.config.remove_section(section)

    def write(self):
        with open(self.config_path, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)


class JianGuoYun:
    ''' 坚果云网盘 '''

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth = username+":"+password
        self.auth = "Basic " + \
            base64.b64encode(self.auth.encode('utf-8')).decode("utf-8")
        self.headers = {
            "Authorization": self.auth
        }
        self.base_url = "https://dav.jianguoyun.com/dav/"

    def put(self, path, file_path):
        ''' 上传文本数据 '''
        log.debug(self.base_url+path)
        log.debug(requests.put(self.base_url+path,
                           headers=self.headers, data=open(file_path, "rb")).text)

    def get(self, path):
        ''' 获取文本数据 '''
        return requests.get(self.base_url+path, headers=self.headers)

    def propfind(self, path):
        ''' 获取列表 '''
        html_str = requests.request(
            'propfind', self.base_url+path, headers=self.headers).text
        html_str = re.sub(r'<[^>]+>', "++", html_str)
        html_str = re.split(r"[++]+", html_str)
        file_path = "/dav/"+path
        if path[-1] != "/":
            file_path += "/"
        file_list = []
        for data in html_str:
            if re.search(r".*"+file_path+r".*", data):
                file_list.append(re.sub(file_path, '', data))
        return file_list


class Other:
    """ 其他 """
    @classmethod
    def set_console(cls, enable):
        """ 设置控制台 """
        if os.name != "nt":
            return False
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd == 0:
            return False
        if enable:
            ctypes.windll.user32.ShowWindow(whnd, 1)
        else:
            ctypes.windll.user32.ShowWindow(whnd, 0)
        return True

    @classmethod
    def match_picname(cls, pic_dir, picname_re):
        pic_list = ""
        filenames = [filename for x in os.walk(
            pic_dir) for filename in x[2]]
        for filename in filenames:
            if picname_re in filename:
                pic_list += os.path.join(pic_dir, filename) + "|"
        if len(pic_list) > 1:
            pic_list = pic_list[:-1]
        return pic_list

    @classmethod
    def get_number(cls, number_text):
        """ 返回所有数字 """
        return int("".join(list(filter(str.isdigit, number_text))))

    @classmethod
    def is_number(cls, number_text):
        """ 判断是否为数字 """
        try:
            number_text = str(number_text)
            if number_text.isdigit():
                return "int"
            float(number_text)
            return "float"
        except:
            return "Nan"

    @classmethod
    def open_app(cls, exec_path,*args):
        """ 打开一个程序 """
        for arg in args:
            exec_path += " " + arg
        Popen(exec_path)

    @classmethod
    def exec_command(cls, command):
        """ 执行命令 """
        return check_output(command,encoding="gbk")

    @classmethod
    def get_netpad_text(cls, note_id=""):
        ''' 获取网络剪贴板的内容,需要json request warnings库
        :param note_id: 剪贴板id
        :return: data || error
        '''
        # 如果标题为空的话获取所有标题
        session = requests.session()
        session.trust_env = False
        netpad_url = "https://netcut.cn/api/note/data/?note_id=" + \
            note_id + "&_=" + str(int(time()))
        # 获取所有该用户名所有文本 verify是否忽略安全证书 我这里不忽略会报错
        warnings.simplefilter("ignore")
        result = session.post(
            netpad_url,
            verify=False,
        ).json()
        if result["error"] == "":
            del result["data"]["log_list"]
            return result["data"]
        else:
            log.error("遇到错误 " + result['error'])
            return result['error']

if __name__ == "__main__":
    log.debug("lib 测试")
    log.info("11")
