#!/usr/bin/env python3

import requests
import json
import re
import pandas
import os
import requests
import logging
if os.name == "nt":
    import win32com.client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from subprocess import Popen,check_output
from random import randint

class Other:
    """ 其他 """
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

class ZhiHu:
    def __init__(self):
        print("开始初始化")
        self.session = requests.session()
        self.driver = None
        self.cookies_path = "input/cookies.txt"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36",
            "Cookie": self.read_cookies()
        }
        self.params = (('include', 'visible_only_to_author,is_visible,paid_info,paid_info_content,admin_closed_comment,reward_info,annotation_action,annotation_detail,collapse_reason,is_normal,is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,created_time,updated_time,review_info,relevant_info,question,excerpt,attachment,relationship.is_authorized,voting,is_thanked,is_author,is_nothelp,is_recognized,is_labeled;mark_infos[*].url;author.badge[*].topics;settings.table_of_content.enabled'),)

    def init_driver(self, port=12306, browser_name=""):
        try:
            options = Options()
            if os.name == "nt":
                self.browser_path = self.get_browser_path(browser_name)
                self.browser_path = self.browser_path.replace(" (x86)", "")
                current_port = self.get_browser_port()
                if not current_port:
                    self.open_browser(f"--remote-debugging-port={port}")
                else:
                    port = current_port
                options.add_experimental_option("debuggerAddress",
                                                f"127.0.0.1:{port}")
                options.binary_location = self.browser_path
                self.driver = webdriver.Chrome(
                    "./input/chromedriver.exe", options=options)
            else:
                browser_name = "Chrome"
                options.add_experimental_option("debuggerAddress",
                                                f"127.0.0.1:{port}")
                self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            logging.exception(e)
            raise Exception(f"{browser_name} 连接失败!")
        logging.debug(f"{browser_name} 连接成功!")

    def get_browser_path(self, browser_name):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            path = os.path.join(os.path.expanduser(r'~'), "Desktop")
            for dirpath, _, filenames in os.walk(path):
                if "Desktop" not in dirpath.split(os.sep)[-1]:
                    continue
                for filename in filenames:
                    if "lnk" not in filename.split(".")[-1]:
                        continue
                    if browser_name in filename:
                        path = dirpath + "\\" + filename
                        break
                break
            shortcut = shell.CreateShortCut(path).TargetPath
            return shortcut
        except Exception as e:
            logging.exception(e)
            raise Exception(f"{browser_name}路径查找失败")

    def get_browser_port(self):
        result = Other.exec_command("tasklist")
        pid_list = []
        for r in result.split("\n"):
            if "chrome.exe" in r:
                pid_list.append(int(re.split(" +", r)[1]))
        result = Other.exec_command("netstat -ano")
        port_list = []
        for r in result.split("\n")[4:]:
            r = re.split(" +", r)
            if len(r) < 4:
                continue
            if int(r[-1]) in pid_list:
                if "127.0.0.1" not in r[2]:
                    continue
                port = int(r[2].split(":")[1])
                port_list.append(port)
        if not port_list:
            return None
        return port_list[0]

    def open_browser(self, *args):
        Other.open_app(self.browser_path, *args)

    def save_cookies(self, cookies):
        with open(self.cookies_path, "w", encoding="utf-8") as f:
            f.write(cookies)

    def read_cookies(self):
        if not os.path.exists(self.cookies_path):
            return ""
        with open(self.cookies_path, "r", encoding="utf-8") as f:
            cookies = f.read()
        if isinstance(cookies, bytes):
            cookies = str(cookies, encoding="utf8")
        cookies = cookies.replace("\r", "")
        cookies = cookies.replace("\n", "")
        return cookies

    def set_cookies(self):
        if not self.driver:
            self.init_driver(12306,"Chrome")
        hisense_cookies = self.driver.get_cookies()
        cookies = ""
        for ck in hisense_cookies:
            cookies += f"{ck['name']}={ck['value']}; "
        cookies = cookies[:-2]
        self.headers["Cookie"] = cookies

    def login(self):
        # 检查cookies 是否可用 正常继续 不正常则获取cookies
        result = None
        for _ in range(2):
            try:
                self.set_cookies()
                self.save_cookies(self.headers["Cookie"])
                return True
            except Exception as e:
                print(e)
                self.set_cookies()
        return False

    # -------------------------------------------------------------------------- #
    # 功能

    def parse_data(self,excel_path):
        data = pandas.read_excel(excel_path,sheet_name='Sheet1')
        return data.to_dict(orient='records')

    def answer(self,question_url,answer_content):
        try:
            qid = re.findall(re.compile('question/([0-9]+)'),question_url)[0]
            url =  'https://www.zhihu.com/api/v4/questions/%s/answers' % qid
            answer_data = {
                "content": f"<p>{answer_content}</p>", "reshipment_settings": "allowed", "comment_permission": "all", "reward_setting": {"can_reward": False},
                "disclaimer_status": "close", "disclaimer_type": "none", "push_activity": True, "table_of_contents_enabled": False
            }
            resp = requests.post(url=url,headers=self.headers,data=json.dumps(answer_data),params=self.params)
            rjson =resp.json()
            if rjson.get('error'):
                raise Exception(rjson['error']['message'])
            return rjson.get('created_time')
        except Exception as e:
            logging.exception(e)

    # -------------------------------------------------------------------------- #

    def main(self):
        try:
            if not self.driver:
                self.init_driver(12306,"Chrome")
            input("确认已经登录到知乎页面后按回车继续")
            if not self.login():
               input("获取登录信息失败~")
               exit(0)
            try:
                start_invertal,end_invertal = 5,10
                answer_invertal = input("输入回答间隔,默认(5-10): ").split("-")
                if len(answer_invertal) > 1:
                    start_invertal,end_invertal = int(answer_invertal[0]),int(answer_invertal[1])
                print("执行脚本")
                for data in self.parse_data('data.xls'):
                    import time
                    if self.answer(data['问题网址'],data['回答内容']):
                        print("回答完毕")
                    else:
                        print("回答失败")
                    time.sleep(randint(start_invertal,end_invertal))
            except Exception as e:
                print("脚本出现以下错误")
                logging.exception(e)
                input("尝试重新运行或者联系作者~")
        except Exception as e:
            print("脚本出现以下错误")
            logging.exception(e)
            input("尝试重新运行或者联系作者~")


if __name__ == "__main__":
    h = ZhiHu()
    h.main()
