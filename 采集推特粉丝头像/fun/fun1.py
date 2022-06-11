try:
    import os
    import sys
    if __name__ == "__main__":
        sys.path.append(os.path.abspath("../"))
except:
    "防止格式化"
    import os
    import sys
import requests
import json
from time import sleep
from random import random
from lib_178me.log import log
from lib_178me.web_auto import WebAutoModule
from lib_178me.funwarp import FunWrap
from lib_178me.other import Other


class Fun1(WebAutoModule):
    def __init__(self, browser_name='Chrome', root_path="."):
        super(Fun1, self).__init__(browser_name)
        # 线程状态
        self.thread_status = "运行"
        # 正在执行
        self.status = "初始化"
        # 参数
        self.params = {}
        # 表格信号
        self.table_signal = None
        self.root_path = root_path

    def init_script_var(self):
        self.index = int(self.params.get("index", 0))
        self.headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "content-type": "application/json",
            "cookie": '',
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "x-csrf-token": "",

        }
        self.proxies = {
            "http": "socks5h://127.0.0.1:1081",
            "https": "socks5h://127.0.0.1:1081"
        }

    def dl(self, message, level="INFO"):
        if hasattr(self, "index"):
            message = f"{message}"
        else:
            message = f"{message}"
        if level == "DEBUG":
            log.debug(message)
        elif level == "INFO":
            log.info(message)
        elif level == "WARNING":
            log.warning(message)
        elif level == "ERROR":
            log.error(message)
        elif level == "EXCEPTION":
            log.exception(message)
        else:
            print(message)

    def exit(self):
        self.quit()
        self.thread_status = "停止"

    def read_params(self, params={}):
        ''' 读取参数 '''
        if params:
            self.params = params.copy()

    def pretreatment(self, task_name=""):
        ''' 预处理函数(每个函数开始之前执行) '''
        if "停止" in self.thread_status:
            self.exit()
            self.thread_status = "停止"
            self.set_table_info(self.status)
            self.dl("停止线程")
            raise Exception("停止线程")
        elif "暂停" in self.thread_status:
            self.thread_status = "暂停"
            self.set_table_info(self.status)
            while "暂停" in self.thread_status:
                sleep(1)
            self.read_params()
        if task_name != "":
            self.dl(task_name + " 开始", "DEBUG")
            self.set_table_info(task_name)

    def set_table_info(self, status_text):
        ''' 设置脚本状态 '''
        self.status = status_text
        if self.table_signal:
            self.table_signal.emit(self.index, {
                "3": self.thread_status,
                "4": status_text,
            })
        else:
            self.dl(status_text)

    """-------------------------------基础函数封装---------------------------------------"""
    @FunWrap("", True)
    def wait_time(self, message: str, time: int):
        """ 等待 """
        for i in range(time, 0, -1):
            self.pretreatment()
            self.set_table_info(f"{message}:{i}秒")
            sleep(1)

    """-------------------------------功能函数---------------------------------------"""

    @FunWrap("读取本地登录信息", True)
    def read_local_login_info(self):
        if not os.path.exists(f"{self.root_path}/file/login_info.txt"):
            with open(f"{self.root_path}/file/login_info.txt", "w", encoding="utf-8") as f:
                f.write("")
        login_info = ""
        with open(f"{self.root_path}/file/login_info.txt", "r", encoding="utf-8") as f:
            login_info = f.read().replace("\r", "").replace("\n", "")
        for ck in login_info.split("; "):
            if ck.split("=")[0] == "ct0":
                self.headers["x-csrf-token"] = ck.split("=")[1]
        return login_info

    @FunWrap("保存登录信息", True)
    def save_login_info(self, login_info):
        with open(f"{self.root_path}/file/login_info.txt", "w", encoding="utf-8") as f:
            f.write(login_info)

    @FunWrap("验证登录信息", True)
    def verify_login_info(self):
        for _ in range(3):
            try:
                if not self.get_user_rest_id("BlvckParis"):
                    raise Exception("登录信息失效!")
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

    @FunWrap("获取登录信息", True)
    def get_login_info(self):
        cookies = ""
        try:
            self.connect()
            switch_result = self.switch_to(url="https://twitter.com")
            if not switch_result:
                self.open_url("https://twitter.com")
            if os.name == "nt":
                import win32gui
                import win32con
                win32gui.MessageBox(None, '确定已经登录后关闭我', '提醒', win32con.MB_OK)
            cookies = []
            for ck in self.driver.get_cookies():
                if ck["name"] == "ct0":
                    self.headers["x-csrf-token"] = ck["value"]
                cookies.append(f"{ck['name']}={ck['value']}; ")
            cookies = "".join(cookies)[:-2]
            log.debug(cookies)
            self.close()
        except Exception as e:
            log.exception(e)
            log.error("获取登录信息出错")
        return cookies

    def get_link_list(self):
        link_list = []
        path = f"{self.root_path}/file/链接.txt"
        if not os.path.exists(path):
            return link_list
        with open(path, "r", encoding="utf8") as f:
            link_list = f.read().replace("\r", "").split("\n")
        link_list = [link for link in link_list if len(link) > 5]
        return link_list

    @FunWrap("获取用户资源ID")
    def get_user_rest_id(self,user_id):
        url = f'https://twitter.com/i/api/graphql/Bhlf1dYJ3bYCKmLfeEQ31A/UserByScreenName?variables={{"screen_name":"{user_id}","withSafetyModeUserFields":true,"withSuperFollowsUserFields":true}}'
        try:
            result = requests.get(url,headers=self.headers,proxies=self.proxies).json()
            return result["data"]["user"]["result"]["rest_id"]
        except Exception as e:
            self.dl(e)
            return None

    @FunWrap("获取关注列表")
    def get_user_followers(self,rest_id,count=30,cursor=None):
        if cursor:
            url = f'https://twitter.com/i/api/graphql/E4u86hU-nCR6P_oNYKt4cw/Followers?variables={{"userId":"{rest_id}","cursor":"{cursor}","count":{count},"includePromotedContent":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":true,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"__fs_responsive_web_like_by_author_enabled":false,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false,"__fs_responsive_web_edit_tweet_api_enabled":false}}'
        else:
            url = f'https://twitter.com/i/api/graphql/E4u86hU-nCR6P_oNYKt4cw/Followers?variables={{"userId":"{rest_id}","count":{count},"includePromotedContent":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":true,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"__fs_responsive_web_like_by_author_enabled":false,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false,"__fs_responsive_web_edit_tweet_api_enabled":false}}'
        try:
            result = requests.get(url,headers=self.headers,proxies=self.proxies).json()
            return result["data"]["user"]["result"]["timeline"]["timeline"]["instructions"][-1]["entries"]
        except Exception as e:
            self.dl(e,"EXCEPTION")
            return None

    @FunWrap("获取粉丝头像和ID", True)
    def get_head_and_id(self):
        path = f"{self.root_path}/file/头像和ID.csv"
        if not os.path.exists(path):
            return []
        with open(path,"r",encoding="utf-8") as f:
            all_head_list = f.read().replace("\r","").split("\n")
        return all_head_list

    @FunWrap("保存粉丝头像和ID", True)
    def save_head_and_id(self, followers):
        head_list = []
        for entry in followers:
            if "itemContent" not in entry["content"]:
                continue
            fs_head = entry["content"]["itemContent"]["user_results"]["result"]["legacy"]["profile_image_url_https"]
            fs_id = entry["content"]["itemContent"]["user_results"]["result"]["legacy"]["screen_name"]
            head_list.append(f"{fs_head},{fs_id}")
        path = f"{self.root_path}/file/头像和ID.csv"
        if not os.path.exists(path):
            all_head = ""
        else:
            with open(f"{self.root_path}/file/头像和ID.csv","r",encoding="utf-8") as f:
                all_head = f.read()
        with open(f"{self.root_path}/file/头像和ID.csv","a",encoding="utf-8") as f:
            for head in head_list:
                if head in all_head:
                    continue
                f.write(head + "\n")

    @FunWrap("获取Bottom cursor", True)
    def get_bottom_cursor(self, followers):
        cursor = None
        followers.reverse()
        for entry in followers:
            if "cursorType" not in entry["content"]:
                continue
            elif "Bottom" != entry["content"]["cursorType"]:
                continue
            elif entry["content"]["value"].split("|")[0] == "0":
                break
            cursor = entry["content"]["value"]
        return cursor

    @FunWrap("获取采集状态", True)
    def get_collect_status(self,username):
        path = f"{self.root_path}/file/采集状态.csv"
        if not os.path.exists(path):
            return None
        with open(path,"r",encoding="utf-8") as f:
            collect_dict = json.load(f)
        if username not in collect_dict:
            return None
        return collect_dict[username]

    @FunWrap("保存采集状态", True)
    def save_collect_status(self,username,collect_status):
        path = f"{self.root_path}/file/采集状态.csv"
        if os.path.exists(path):
            with open(path,"r",encoding="utf-8") as f:
                collect_dict = json.load(f)
        else:
            collect_dict = {}
        collect_dict[username] = collect_status
        with open(f"{self.root_path}/file/采集状态.csv","w",encoding="utf-8") as f:
            json.dump(collect_dict,f,ensure_ascii=False,indent=4)

    @FunWrap("下载头像", True)
    def download_head(self,head):
        url,name = head.split(",")
        head_path = f"{self.root_path}/头像/{name}.jpg"
        if os.path.exists(head_path):
            self.dl("已经下载过了，自动跳过")
            return False
        r = requests.get(url,headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"},proxies=self.proxies)
        with open(head_path, 'wb') as f:
            f.write(r.content)
        return True

    """------------------------------流程函数---------------------------------------"""

    def help(self):
        self.dl("每次爬取数量(默认50):")
        self.params["count"] = Other.is_number(input())
        if not isinstance(self.params["count"], int):
            self.dl("未填写或填写有误,默认为50")
            self.params["count"] = 50

    def collect_info(self):
        link_list = self.get_link_list()
        for link in link_list:
            rest_id = self.get_user_rest_id(link)
            cursor = self.get_collect_status(link)
            count = self.params.get("count",50)
            if not rest_id:
                continue
            if cursor and "采集完成" in cursor:
                continue
            while True:
                self.dl(f"{link} 采集进度: {cursor}")
                followers = self.get_user_followers(rest_id,count=count,cursor=cursor)
                if not followers:
                    self.dl("未获取到粉丝列表,退出采集","WARNING")
                    break
                self.save_head_and_id(followers)
                cursor = self.get_bottom_cursor(followers)
                self.save_collect_status(link,cursor)
                if not cursor:
                    self.save_collect_status(link,"采集完成")
                    self.dl(f"{link} 采集完成")
                    break
                sleep(random())

    def download_all_head(self):
        all_head_list = self.get_head_and_id()
        self.dl(f"总数:{len(all_head_list)}")
        for i,head in enumerate(all_head_list):
            try:
                if len(head) < 5:
                    continue
                self.dl(f"下载进度 {i}:  {head}")
                if self.download_head(head):
                    sleep(random())
            except Exception as e:
                self.dl(e,"EXCEPTION")

    def main(self):
        self.thread_status = "运行"
        if "fun" in os.getcwd():
            self.root_path = ".."
        self.init_script_var()
        self.dl("""采集推特粉丝头像ID
1. 采集粉丝头像
2. 下载粉丝头像
执行功能(例如 1):""")
        code = input().strip()
        if code == "1":
            self.help()
            self.headers["Cookie"] = self.read_local_login_info()
            self.verify_login_info()
            self.collect_info()
        elif code == "2":
            self.download_all_head()
        else:
            self.dl("功能选择错误!","ERROR")
        self.dl("脚本结束")
        input()

    @FunWrap("测试", True)
    def test(self, params={}):
        self.thread_status = "运行"
        self.init_script_var()
        self.headers["Cookie"] = self.read_local_login_info()
        #  self.connect()
        print(self.headers)
        self.verify_login_info()
        self.download_head("https://pbs.twimg.com/profile_images/1508340577531678722/MUKEB6SB_normal.jpg,test")

if __name__ == "__main__":
    print("自动化测试")
    qq_login = Fun1(root_path="..")
    qq_login.test({
        "index": 1,
    })
