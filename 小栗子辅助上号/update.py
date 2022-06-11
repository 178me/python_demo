'''
@author: 178me
@description: 为了远程用户代码和我本地代码保持一致
'''
import re
import os
import base64
import json
import configparser
import requests

class Config():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.getcwd() + os.sep + "config.ini"
        if os.path.exists(self.config_path):
            self.config.read(self.config_path, encoding="utf-8")

    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get(self, section=None, key=None):
        if key:
            if not self.config.has_section(section):
                return None
            return self.config.get(section, key)
        if section:
            if not self.config.has_section(section):
                return None
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
        self.session = requests.session()
        self.session.trust_env = False
        self.username = username
        self.password = password
        self.auth = username+":"+password
        self.auth = "Basic " + \
            base64.b64encode(self.auth.encode('utf-8')).decode("utf-8")
        self.headers = {
            "Authorization": self.auth
        }
        self.base_url = "https://dav.jianguoyun.com/dav/"

    def put(self, path, text):
        ''' 上传文本数据 '''
        self.session.put(self.base_url+path, headers=self.headers, data=text)

    def get(self, path):
        ''' 获取文本数据 '''
        return self.session.get(self.base_url+path, headers=self.headers)

    def propfind(self, path):
        ''' 获取列表 '''
        html_str = self.session.request(
            'propfind', self.base_url+path, headers=self.headers).text
        html_str = re.sub(r'<[^>]+>', "++", html_str)
        html_str = re.split(r"[++]+", html_str)
        file_path = "/dav/"+path
        if path[-1] != "/":
            file_path += "/"
        file_list = []
        for data in html_str:
            if re.search(r".*"+file_path+r".*", data):
                file_name = re.sub(file_path, '', data)
                if file_name == "":
                    continue
                file_list.append(file_name)
        return file_list


def download_file(download_url, file_name):
    sep = os.sep
    try:
        session = requests.session()
        session.trust_env = False
        print("下载文件中,请耐心等待")
        content = session.get(download_url).content
        with open(f'{os.getcwd()}{sep}{file_name}', 'wb') as file_writer:
            file_writer.write(content)
    except Exception as e:
        print(f"下载 {file_name} 文件出错")

def get_lzy_link(url):
    global lzy
    if url.find("lanzou") == -1:
        print('不是蓝奏云链接')
        return None
    pwd = ""
    if url.find(" 密码:") != -1:
        pwd = url.split(" 密码:")[1]
        url = url.split(" 密码:")[0]
    elif url.find("\n密码:") != -1:
        pwd = url.split("\n密码:")[1]
        url = url.split("\n密码:")[0]
    #  https://wws.lanzoui.com/i1ZLGraavmf 密码:8rfb
    link = lzy.get_durl_by_url(url, pwd)
    if link[0] == 0:
        return (link[2], link[1])
    else:
        return None


def write_update_config(jgy, path):
    global config_file
    version = "1.0.0"
    config = {
        "version": version,
        "download_url": "https://wws.lanzoui.com/ilQAxtrbpuh 密码:bzjr",
    }
    config = json.dumps(config)
    config_file.set("app", "version", version)
    jgy.put(path, config)
    config_file.write()
    exit(0)

if __name__ == '__main__':
    try:
        from lanzou.api import LanZouCloud
        from pymsgbox import confirm, alert
        lzy = LanZouCloud()
        print(dir(lzy))
        config_file = Config()
        jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        #  write_update_config(jgy,"python_project/qq_login/update_config.txt")
        config = json.loads(
            jgy.get("python_project/qq_login/update_config.txt").text)
        current_version = config_file.get("app", "version")
        version = config["version"]
        download_url = config["download_url"]
        if current_version < version:
            result = confirm(f"检查到新版本 {version} ,是否更新?",
                             "检查更新", ["立即更新", "下次再说"])
        else:
            alert(f"最新版本为 {version} ,当前版本为 {current_version} ,不需要更新!", "检查更新")
            exit(0)
        if "更新" in result:
            download_url = get_lzy_link(download_url)
            if download_url:
                download_file(download_url[0], download_url[1])
                config_file.set("app", "version", version)
                config_file.write()
    except Exception as e:
        print(e)
        input("脚本执行异常,回车退出")
