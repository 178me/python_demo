try:
    import os
    import sys
    sys.path.append(os.path.join(os.path.abspath("./"), "lib_178me"))
except:
    "防止格式化"
    import os
import time
import requests
from openpyxl import load_workbook
from lib_178me.log import log
from lib_178me.funwarp import FunWrap
from pprint import pprint
from random import choice, randint


USERAGENT = [
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)",
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "
]

class Fun1:
    def __init__(self) -> None:
        self.init_var()

    def init_var(self):
        self.session = requests.session()
        self.headers = {
            "User-Agent": choice(USERAGENT)
        }
        self.headers["Cookie"] = self.read_local_login_info()
        self.sid = None

    def pretreatment(self, task_name):
        if task_name != "":
            log.info(task_name + " 开始")

    @FunWrap("读取本地登录信息", True)
    def read_local_login_info(self):
        if not os.path.exists("./out/login_info.txt"):
            with open("./out/login_info.txt", "w", encoding="utf-8") as f:
                f.write("")
        login_info = ""
        with open("./out/login_info.txt", "r", encoding="utf-8") as f:
            login_info = f.read()
        login_info = login_info.replace("\r", "").replace("\n", "")
        return login_info

    @FunWrap("保存登录信息", True)
    def save_login_info(self, login_info):
        with open("./out/login_info.txt", "w", encoding="utf-8") as f:
            f.write(login_info)

    @FunWrap("获取登录信息", True)
    def get_login_info(self):
        cookies = ""
        web = None
        try:
            web = WebAutoModule("Chrome")
            if os.name == "nt":
                import win32gui
                import win32con
                win32gui.MessageBox(None, '确定已经登录后关闭我', '提醒', win32con.MB_OK)
            cookies = [
                f"{ck['name']}={ck['value']}; " for ck in web.driver.get_cookies()]
            for ck in web.driver.get_cookies():
                if ck['name'] == "sid":
                    self.sid = ck['value']
                cookies += f"{ck['name']}={ck['value']}; "
            cookies = "".join(cookies)[:-2]
            log.debug(cookies)
            if self.sid is None:
                raise Exception("未获取到sid")
        except Exception as e:
            log.exception(e)
            log.error("获取登录信息出错")
        return cookies

    @FunWrap("验证登录信息", True)
    def verify_login_info(self):
        for _ in range(3):
            try:
                self.set_user_info()
                log.info("登录信息验证成功")
                return True
            except Exception as e:
                if "登录信息失效!" in str(e):
                    login_info = self.get_login_info()
                    self.save_login_info(login_info)
                    self.headers["Cookie"] = self.read_local_login_info()
                else:
                    log.exception(e)
                    log.error("验证登录信息出错")
        raise Exception("验证登录信息出错")

    def search_message(self, date_rang):
        print("搜索指定邮件")
        data = {
            "start": (None, 0),
            "limit": (None, 100),
            "fid": (None, 0),  # 文件夹
            #  "sentDate": (None, "2022-01-15:2022-01-16"),  # 时间
            "sentDate": (None, date_rang),  # 时间
        }
        method = "searchMessages"
        url = f'https://mail.hisense.com/coremail/XT5/jsp/mail.jsp?func={method}&sid={self.sid}'
        result = self.session.post(url, data=data, headers=self.headers)
        result = result.json()
        if "S_OK" not in result["code"]:
            raise Exception(f"请求失败:{result['code']}")
        #  print(result)
        return result["var"]

    def get_attach_list(self, mid):
        print("读取邮件附件地址")
        data = {
            "mid": (None, mid)
        }
        method = "readMessage"
        url = f'https://mail.hisense.com/coremail/XT5/jsp/mail.jsp?func={method}&sid={self.sid}'
        result = self.session.post(url, data=data, headers=self.headers)
        result = result.json()
        if "S_OK" not in result["code"]:
            raise Exception(f"请求失败:{result['code']}")
        attach_list = []
        for attach in result["var"]["mail"]["attachments"]:
            if "filename" in attach:
                if "image" in attach["contentType"]:
                    continue
                attach_list.append({
                    "filename": attach["filename"],
                    "url": f"https://mail.hisense.com/coremail/common/preview/preview.jsp?part={attach['id']}&mode=preview&mboxa=&mid={mid}"
                })
        return attach_list

    def main(self):
        log.debug("测试开始")


if __name__ == '__main__':
    pass
