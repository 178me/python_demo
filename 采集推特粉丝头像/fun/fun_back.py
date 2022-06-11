try:
    import os
    import sys
    if __name__ == "__main__":
        sys.path.append(os.path.abspath("../"))
except:
    "防止格式化"
    import os
    import sys
import json
import datetime
from os import link
from time import sleep
from random import randint
from imbox import Imbox
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
        self.excel_path = f"{self.root_path}/file/社工名单.xlsx"

    def init_object(self):
        pass

    def init_script_var(self):
        self.index = int(self.params.get("index", 0))
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        }
        self.headers2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
        }
        self.user_id = ""
        self.token = ""

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
        self.dl(json.dumps(self.params, ensure_ascii=False, indent=4))
        self.index = int(self.params.get("index", 0))

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

    @FunWrap("", True)
    def get_account_list(self):
        """ 获取账号列表 """
        account_list = []
        if not os.path.exists(self.root_path + "/file/账号列表.txt"):
            return account_list
        with open(self.root_path + "/file/账号列表.txt", "r", encoding="utf-8") as f:
            for account_info in f.read().replace("\r", "").split("\n"):
                if len(account_info) < 5:
                    continue
                account_info = account_info.split(":")
                account_list.append({
                    "steam_account": account_info[0],
                    "steam_password": account_info[1],
                    "steam_email_account": account_info[2],
                    "steam_email_password": account_info[3],
                    "orgin_account": account_info[4],
                    "orgin_password": account_info[5],
                    "orgin_email_password": account_info[6],
                    "finish_status": ""
                })
        return account_list

    @FunWrap("", True)
    def filter_account_list(self, account_list):
        """ 筛选账号列表 """
        if not os.path.exists(self.root_path + "/file/完成列表.txt"):
            return account_list
        with open(self.root_path + "/file/完成列表.txt", "r", encoding="utf-8") as f:
            for account_info in f.read().replace("\r", "").split("\n"):
                if len(account_info) < 5:
                    continue
                for account in account_list:
                    if ":".join([str(info) for info in account.values()]) in account_info:
                        account_list.remove(account)
                        break
        return account_list

    @FunWrap("", True)
    def get_email_code(self, username, password):
        """ 获取邮箱接受的验证码 """
        with Imbox('mail.tk-home.cn', username=username, password=password, ssl=False) as imbox:
            begin_time = datetime.datetime.now() - datetime.timedelta(seconds=100)
            #  begin_time = datetime.datetime.now() - datetime.timedelta(days=1)
            for _ in range(20):
                messages = imbox.messages(
                    sent_from='EA@e.ea.com', date__gt=begin_time)
                for _, message in messages:
                    email_date = message.parsed_date + \
                        datetime.timedelta(hours=14)
                    if email_date < begin_time:
                        continue
                    if len(Other.get_number(message.subject)) == 6:
                        #  if "您的EA验证码是：" in message.subject:
                        return Other.get_number(message.subject)
                sleep(3)
        return None

    @FunWrap("进入Steam 登录页", True)
    def join_steam_login_page(self):
        """ 进入Steam 登录页 """
        self.open_url("https://myaccount.ea.com/cp-ui/aboutme/index?")
        self.find_elem("//img[@class='right btn-steam-login']", is_click=True)
        assert self.switch_to(title="Steam 社区", find_time=15)

    @FunWrap("登录Steam", True)
    def login_steam(self, account, password):
        """ 登录Steam """
        self.switch_to(title="Steam 社区",)
        account_elem = self.find_elem(
            "//input[@id='steamAccountName']", is_click=True, find_time=0.1)
        if account_elem:
            self.input_text(account_elem, account)
        password_elem = self.find_elem(
            "//input[@id='steamPassword']", is_click=True, find_time=0.1)
        if password_elem:
            self.input_text(password_elem, password)
        self.find_elem(
            "//input[@id='imageLogin']", is_click=True, find_time=0.5)
        assert self.find_elem(
            "//button[@value='allow']/span", is_click=True, find_time=15)

    @FunWrap("建立你的EA账号信息", True)
    def build_ea_account_info(self):
        """ 建立你的EA账号信息 """
        self.switch_to(url="http", find_time=5)
        country_elem = self.find_elem(
            "//select[@id='clientreg_country-selctrl']", find_time=1)
        assert country_elem
        self.select_cmb(country_elem, -1)
        month_elem = self.find_elem(
            "//select[@id='clientreg_dobmonth-selctrl']", find_time=0.1)
        self.select_cmb(month_elem, -1)
        day_elem = self.find_elem(
            "//select[@id='clientreg_dobday-selctrl']", find_time=0.1)
        self.select_cmb(day_elem, -1)
        year_elem = self.find_elem(
            "//select[@id='clientreg_dobyear-selctrl']", find_time=0.1)
        self.select_cmb(year_elem, randint(20, 35))
        assert self.find_elem(
            "//a[@id='countryDobNextBtn' and @aria-disabled='false']", is_click=True, find_time=0.1)

    @FunWrap("创建EA账号", True)
    def create_ea_account(self, account):
        """ 创建EA账号 """
        ea_account_elem = self.find_elem(
            "//input[@id='email']", is_click=True, find_time=1)
        assert ea_account_elem
        self.input_text(ea_account_elem, account)
        assert self.find_elem(
            "//a[@id='basicInfoNextBtn' and @aria-disabled='false']", is_click=True, find_time=1)

    @FunWrap("EA账号已存在", True)
    def account_exists(self):
        """ EA账号已存在 """
        return self.find_elem(
            "//a[@id='continue']", is_click=True, find_time=1)

    @FunWrap("发送邮箱验证码", True)
    def send_email_code(self):
        """ 发送邮箱验证码 """
        assert self.find_elem(
            "//a[@id='btnSendCode']", is_click=True, find_time=1)

    @FunWrap("填写邮箱验证码", True)
    def input_email_code(self, account, password):
        """ 填写邮箱验证码 """
        email_code = self.get_email_code(account, password)
        code_elem = self.find_elem(
            "//input[@id='twoFactorCode']", is_click=True, find_time=1)
        if not email_code:
            return False
        self.input_text(code_elem, email_code)
        assert self.find_elem(
            "//a[@id='btnSubmit']", is_click=True, find_time=1)

    @FunWrap("审阅条款", True)
    def review_our_terms(self):
        """ 审阅条款 """
        self.find_elem(
            "//label[@for='readAccept']", is_click=True, find_time=1)
        self.find_elem(
            "//a[@id='btnNext']", is_click=True, find_time=0.1)

    @FunWrap("链接EA到Steam", True)
    def link_ea_to_steam(self):
        """ 链接EA到Steam """
        assert self.find_elem(
            "//form[@id='AccountLinkConfirmationForm']/a[@id='continue']", is_click=True, find_time=1)

    @FunWrap("链接EA到Steam", True)
    def get_start(self):
        """ 链接EA到Steam """
        assert self.find_elem(
            "//form[@id='accountLinkEndForm']/a[@id='continueBtn']", is_click=True, find_time=1)

    @FunWrap("检查是否完成", True)
    def is_finish(self):
        """ 检查是否完成 """
        return self.find_elem(
            "//h1[contains(text(),'我的帐户: 关于我 ')]", is_click=True, find_time=1)

    def save_finish_account(self, account_info):
        with open(self.root_path + "/file/完成列表.txt", "a", encoding="utf-8") as f:
            f.write(":".join([str(info)
                    for info in account_info.values()]) + "\n")

    def jump_follow(self, url):
        self.open_url(url)

    """------------------------------流程函数---------------------------------------"""

    def help(self):
        my_password = ""

    def run(self, account):
        self.new()
        while True:
            try:
                self.dl(account)
                self.join_steam_login_page()
                self.login_steam(account["steam_account"],
                                 account["steam_password"])
                self.build_ea_account_info()
                self.create_ea_account(account["orgin_account"])
                self.account_exists()
                self.send_email_code()
                self.input_email_code(
                    account["orgin_account"], account["orgin_email_password"])
                #  self.review_our_terms()
                self.link_ea_to_steam()
                self.get_start()
                if not self.is_finish():
                    raise Exception("创建失败")
                account["finish_status"] += "关联成功"
                self.save_finish_account(account)
                break
            except Exception as e:
                #  self.dl(e,"EXCEPTION")
                page_title = self.find_elems("//h1")
                if page_title:
                    for title in page_title:
                        if len(title.text) < 2:
                            continue
                        account["finish_status"] += title.text.replace(
                            "\n", "")
                        self.save_finish_account(account)
            self.dl(account["finish_status"])
            break
        self.quit()
        return True

    def main(self, params={}):
        self.thread_status = "运行"

    #  @FunWrap("获取头像", True)
    def get_all_head_portrait(self):
        head_portrait = []
        elems = self.find_elems(
            "//div[@data-testid='UserCell']//a[@role='link' and @aria-hidden='true']")
        for elem in elems:
            try:
                name = elem.get_attribute("href").replace(
                    "https://twitter.com/", "")
                head_portrait.append({
                    "name": name,
                    "elem": elem
                })
            except:
                pass
        return head_portrait

    #  @FunWrap("下载头像", True)
    def download_head_portrait(self, head):
        try:
            head_path = f"{self.root_path}/头像/{head['name']}.png"
            if os.path.exists(head_path):
                return True
            head["elem"].screenshot(head_path)
            return True
        except:
            self.dl("保存头像出错")
            pass
        return False

    #  @FunWrap("下一页", True)
    def page_down(self, temp_height=0):
        try:
            #  elem = self.find_elem("/html/body", find_time=1)
            #  if not elem:
            #      return temp_height
            #  self.press(elem, self.Keys.PAGE_DOWN)
            self.driver.execute_script(
                "document.documentElement.scrollTop = arguments[0] + window.innerHeight;", temp_height)
            for _ in range(3):
                # 获取当前滚动条距离顶部的距离
                check_height = self.driver.execute_script(
                    "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
                # 如果两者相等说明到底了
                if check_height == temp_height:
                    sleep(5)
                    continue
                return check_height
            return False
        except:
            return 0

    def get_link_list(self):
        link_list = []
        path = f"{self.root_path}/file/链接.txt"
        print(os.path.exists("../file/链接.txt"))
        if not os.path.exists(path):
            return link_list
        print(path)
        with open(path, "r", encoding="utf8") as f:
            link_list = f.read().replace("\r", "").split("\n")
        link_list = [link for link in link_list if len(link) > 5]
        return link_list

    @FunWrap("测试", True)
    def test(self, params={}):
        self.thread_status = "运行"
        self.connect()
        self.read_params(params)
        link_list = self.get_link_list()
        print(link_list)
        for link in link_list:
            self.jump_follow(link)
            temp_height = self.driver.execute_script(
                "return document.documentElement.scrollTop")
            while True:
                try:
                    head_portrait = self.get_all_head_portrait()
                    for head in head_portrait:
                        self.download_head_portrait(head)
                    temp_height = self.page_down(temp_height)
                    if not temp_height:
                        if not self.find_elem("//span[contains(text(),'Retry')]",is_click=True):
                            self.jump_follow(link)
                            self.quit()
                            break
                    print(temp_height)
                except:
                    print("网页异常崩溃")
                    if os.name != "nt":
                        self.focu_kill()
                        self.open_browser(f"--remote-debugging-port=12306")
                    self.connect()
                    self.jump_follow(link)


if __name__ == "__main__":
    print("自动化测试")
    qq_login = Fun1(root_path="..")
    qq_login.test({
        "index": 1,
    })
