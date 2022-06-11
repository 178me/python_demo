import os
import ctypes
import requests
from warnings import simplefilter
from time import time
from subprocess import Popen, check_output,run


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
        try:
            return "".join(list(filter(str.isdigit, number_text)))
        except:
            return 0

    @classmethod
    def is_number(cls, number_text):
        """ 判断是否为数字 """
        try:
            number_text = str(number_text)
            if number_text.isdigit():
                return int(number_text)
            return float(number_text)
        except:
            return number_text

    @classmethod
    def open_app(cls, exec_path, *args):
        """ 打开一个程序 """
        command = exec_path
        for arg in args:
            command += " " + arg
        if os.name == "nt":
            Popen(command)
        else:
            os.popen(command)

    @classmethod
    def exec_command(cls, command):
        """ 执行命令 """
        return check_output(command, encoding="gbk")

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
        simplefilter("ignore")
        result = session.post(
            netpad_url,
            verify=False,
        ).json()
        if result["error"] == "":
            del result["data"]["log_list"]
            return result["data"]
        else:
            print("遇到错误 " + result['error'])
            return result['error']


if __name__ == "__main__":
    #  print(check_output("/usr/bin/chromium",encoding="utf-8"))
    run(['chromium','--remote-debugging-port=12306'])
    os.popen('chromium --remote-debugging-port=12306')


