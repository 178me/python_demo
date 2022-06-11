import os
import ctypes
from subprocess import Popen, check_output

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
            return int("".join(list(filter(str.isdigit, number_text))))
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
        for arg in args:
            exec_path += " " + arg
        Popen(exec_path)

    @classmethod
    def exec_command(cls, command):
        """ 执行命令 """
        return check_output(command, encoding="gbk")

if __name__ == "__main__":
    result = Other.is_number("dsfja")
    if isinstance(result,str):
        print("fds")
    print(result)
