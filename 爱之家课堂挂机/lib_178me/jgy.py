from base64 import b64encode
import requests
import re

class JianGuoYun:
    ''' 坚果云网盘 '''

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth = username+":"+password
        self.auth = "Basic " + \
            b64encode(self.auth.encode('utf-8')).decode("utf-8")
        self.headers = {
            "Authorization": self.auth
        }
        self.base_url = "https://dav.jianguoyun.com/dav/"

    def put(self, path, file_path):
        ''' 上传文本数据 '''
        requests.put(self.base_url+path,
                           headers=self.headers, data=open(file_path, "rb")).text
        print("推送成功")

    def get(self, path):
        ''' 获取文本数据 '''
        return requests.get(self.base_url+path, headers=self.headers)

    def propfind(self, path):
        ''' 获取列表 '''
        html_str = requests.request(
            'propfind', self.base_url+path, headers=self.headers).text
        html_str = re.sub(r'<[^>]+>', "++", html_str)
        html_str = re.split(r"[++]+", html_str)
        file_path = "/dav/" + path
        if path[-1] != "/":
            file_path += "/"
        file_list = []
        for data in html_str:
            if re.search(r".*"+file_path+r".*", data):
                file_list.append(re.sub(file_path, '', data))
        return file_list

