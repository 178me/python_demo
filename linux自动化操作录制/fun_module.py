import requests
import json
import random
from time import sleep
from auto_moudle import AutoMationModule
from lib import FunWrap, log


class VncAuto(AutoMationModule):
    def __init__(self):
        # 初始化父类方法
        super(VncAuto, self).__init__()
        # 脚本执行状态
        self.debug_mode = True
        self.index = "Arch"
        self.status = "初始化"
        # 线程状态
        self.thread_status = "运行"
        self.params = {}
        self.message_list = []

    def exit(self):
        self.thread_status = "停止"

    def pretreatment(self, task_name=""):
        ''' 预处理函数(每个函数开始之前执行) '''
        if "停止" in self.thread_status:
            self.thread_status = "停止"
            self.dl("停止线程")
            raise Exception("停止线程")
        elif "暂停" in self.thread_status:
            self.thread_status = "暂停"
            self.dl("暂停线程")
            while "暂停" in self.thread_status:
                sleep(1)
        if task_name != "":
            self.dl(task_name + " 开始")

    @FunWrap("切换桌面buffer", False)
    def switch_buffer(self, buffer_index):
        self.hot_key("winleft", str(buffer_index))

    @FunWrap("切换页面", False)
    def switch_next_page(self, way: str = "right"):
        self.hot_key("winleft", way)

    @FunWrap("进入发送文件页面", False)
    def join_send_file_page(self):
        self.move(980, 67)
        self.find_image("send_file_icon.bmp", find_time=1,
                        sim=0.9, is_click=True)

    @FunWrap("点击发送文件按钮", False)
    def click_send_file_btn(self):
        self.find_image("send_file_btn.bmp", find_time=1,
                        sim=0.9, is_click=True)

    @FunWrap("输入发送文件路径", False)
    def input_send_file_path(self, file_path: str):
        self.find_image("path_lable.bmp", offset=(100, 0),
                        find_time=1, sim=0.9, is_click=True)
        self.hot_key("ctrl", "a")
        self.input_text(file_path)

    @FunWrap("确定发送文件", False)
    def sure_send_file(self):
        self.find_image("ok.bmp", find_time=1, sim=0.9, is_click=True)

    @FunWrap("关闭发送文件页面", False)
    def close_send_file_page(self):
        if self.find_image("send_file_page.bmp", find_time=1, sim=0.9, is_click=True):
            self.hot_key("winleft", "shift", "q")

    @FunWrap("返回桌面", False)
    def back_desktop(self):
        self.hot_key("leftwin", "d")
        sleep(1)
        self.switch_next_page()

    @FunWrap("VNC发送文件", False)
    def vnc_send_file(self):
        self.join_send_file_page()
        self.click_send_file_btn()
        self.input_send_file_path("/home/yzl178me/source/send_file/配置工具.zip")
        self.sure_send_file()
        self.close_send_file_page()

    @FunWrap("自动输入密码", False)
    def temp_fun(self):
        self.hot_key("leftwin", "shift", "space")
        sleep(0.3)
        page = self.find_image("ld_title.bmp", x1=817, offset=(0, 190),
                               find_time=1, sim=0.9, is_click=True)
        sleep(0.5)
        self.auto.typewrite("18155411159")
        page = self.find_image("ld_title.bmp", x1=817, offset=(0, 240),
                               find_time=1, sim=0.9, is_click=True)
        sleep(0.5)
        self.auto.typewrite("jie123456")
        #  self.auto.typewrite("18155411159")

    @FunWrap("", False)
    def wait(self,sec,is_while=False):
        if is_while:
            for _ in range(sec):
                self.wait(1)
                sec -= 1
                self.dl(f"倒计时:{sec}")
        else:
            sleep(sec)


    def unit_chat(self,chat_input, user_id="88888"):
        client_id = "hIkC0fSxfQX17dGsbVcUGYzx"
        client_secret = "wluN6dVLGjUlnyvxtiSzQzchrHnv4O2K"
        """
        description:调用百度UNIT接口，回复聊天内容
        Parameters
          ----------
          chat_input : str
              用户发送天内容
          user_id : str
              发起聊天用户ID，可任意定义
        Return
          ----------
          返回unit回复内容
        """
        # 设置默认回复内容,  一旦接口出现异常, 回复该内容
        chat_reply = "不好意思，俺们正在学习中，随后回复你。"
        # 根据 client_id 与 client_secret 获取access_token
        url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s" % (
        client_id, client_secret)
        res = requests.get(url)
        access_token = eval(res.text)["access_token"]
        # 根据 access_token 获取聊天机器人接口数据
        unit_chatbot_url = "https://aip.baidubce.com/rpc/2.0/unit/service/chat?access_token=" + access_token
        # 拼装聊天接口对应请求发送数据，主要是填充 query 值
        post_data = {
                    "log_id": str(random.random()),
                    "request": {
                        "query": chat_input,
                        "user_id": user_id
                    },
                    "session_id": "",
                    "service_id": "S30762",
                    "version": "2.0"
                }
        # 将封装好的数据作为请求内容, 发送给Unit聊天机器人接口, 并得到返回结果
        res = requests.post(url=unit_chatbot_url, json=post_data)


        # 获取聊天接口返回数据
        unit_chat_obj = json.loads(res.content)
        # print(unit_chat_obj)
        # 打印返回的结果
        # 判断聊天接口返回数据是否出错 error_code == 0 则表示请求正确
        if unit_chat_obj["error_code"] != 0: return chat_reply
        # 解析聊天接口返回数据，找到返回文本内容 result -> response_list -> schema -> intent_confidence(>0) -> action_list -> say
        unit_chat_obj_result = unit_chat_obj["result"]
        unit_chat_response_list = unit_chat_obj_result["response_list"]
        # 随机选取一个"意图置信度"[+response_list[].schema.intent_confidence]不为0的技能作为回答
        unit_chat_response_obj = random.choice(
           [unit_chat_response for unit_chat_response in unit_chat_response_list if
            unit_chat_response["schema"]["intent_confidence"] > 0.0])
        unit_chat_response_action_list = unit_chat_response_obj["action_list"]
        unit_chat_response_action_obj = random.choice(unit_chat_response_action_list)
        self.dl([value["say"] for value in unit_chat_response_action_list])
        unit_chat_response_say = unit_chat_response_action_obj["say"]
        return unit_chat_response_say

    @FunWrap("读取消息列表", False)
    def read_message(self):
        with open("./message/message1.json","r") as f:
            self.message_list = json.load(f)

    @FunWrap("自动编辑消息", False)
    def auto_input_message(self):
        #  print(self.auto.prompt(text="请输入文字",title="提示",default="大家都认真拼起來了"))
        #  return 
        input_list = self.find_images("gift.bmp", find_time=1, sim=0.99)
        if input_list:
            for i,v in enumerate(input_list):
                x1,y1,x2,y2 = v.left - 320,v.top - 50,v.left,v.top + 50
                if self.find_image("faxiaoxi.bmp",x1=x1,y1=y1,x2=x2,y2=y2, find_time=0.1, sim=0.9, is_click=False):
                    rep_message = None
                    for _ in range(20):
                        if not rep_message:
                            random_message = random.choice(self.message_list)
                            #  random_message = ""
                        else:
                            random_message = rep_message
                        message = self.auto.prompt(text=f"第{i+1}个窗口",title="请输入文字",default=random_message)
                        rep_message = None
                        if not message:
                            continue
                        if message.find("`1") != -1:
                            message = message.replace("`1`","")
                            message = message.replace("`1","")
                            rep_message = self.unit_chat(message)
                            continue
                        elif message.find("`2") != -1:
                            break
                        self.click(v.left,v.top+10)
                        sleep(0.1)
                        self.click(v.left,v.top+10)
                        self.input_text(message)
                        if message in self.message_list:
                            self.message_list.remove(message)
                        self.dl(f"剩余{len(self.message_list)}个消息")
                        break

    @FunWrap("自动发送消息", False)
    def auto_send_meg(self):
        #  print(self.find_images("send_enable.bmp", find_time=5, sim=0.99))
        #  return 
        # 500 100
        while True:
            self.auto_input_message()
            send_list = self.find_images("send_enable.bmp", find_time=3, sim=0.99)
            if send_list:
                for v in send_list:
                    x1,y1,x2,y2 = v.left - 450,v.top - 200,v.left + 100,v.top + 20
                    print(x1,y1,x2,y2)
                    if self.find_image("faxiaoxi.bmp",x1=x1,y1=y1,x2=x2,y2=y2, find_time=1, sim=0.9, is_click=False):
                        self.dl("请编辑好消息!")
                    else:
                        #  self.find_image("gift.bmp",x1=x1,y1=y1,x2=x2,y2=y2, find_time=1, sim=0.9, is_click=True,offset=(-50,0))
                        #  self.press("esc")
                        #  sleep(0.1)
                        #  self.press("enter")
                        self.dl("发送消息!")
                        #  self.wait(random.randint(4,8),True)
            self.wait(0.1)

    def main(self, params):
        self.thread_status = "运行"
        self.params = params
        self.dl(params)
        self.read_message()
        #  for _ in range(8):
        #  self.back_desktop()
        self.auto_send_meg()
        #  self.auto_input_message()
        #  sleep(1)
        #  self.switch_next_page()
        self.exit()

    @FunWrap("测试", True)
    def test(self, params):
        self.dl(params)
        #  self.message_list.remove("冲起来")
        print(self.message_list)
        #  self.auto_input_message()
        self.auto.confirm(text="123456",title="abcd",buttons=["ok","cancel","x"])


if __name__ == "__main__":
    print("自动化测试")
    module_object = VncAuto()
    module_object.test({
        "index": 4,
        "hwnd": 12849,
    })
