try:
    import os
    import sys
    sys.path.append(os.path.join(os.path.abspath("./"), "lib_178me"))
except:
    "防止格式化"
    import os
import time
import itchat
from itchat.content import TEXT, PICTURE,  ATTACHMENT, VIDEO
from openpyxl import load_workbook
from lib_178me.log import log,modify_log_level
from pprint import pprint
modify_log_level(20)
GROUP_NAME = "关键字提醒群"
FILE_PATH = "./文件"
# 联系人列表和关键字列表
contact_list = []
keyword_list = []


def read_config():
    global contact_list
    global keyword_list
    book = load_workbook("./config/监听表.xlsx")
    sheet = book['监听列表']
    for cell in sheet["A"]:
        if cell.row == 1:
            continue
        if cell.value:
            contact_list.append(cell.value)
    for cell in sheet["B"]:
        if cell.row == 1:
            continue
        if cell.value:
            keyword_list.append(cell.value)
    log.debug(contact_list)
    log.debug(keyword_list)


def download_file(msg):
    """ 下载文件
    1. 检查路径
    2. 检查文件命名
    """
    save_file_dir = f"{FILE_PATH}/{msg['User']['NickName']}"
    if not os.path.exists(save_file_dir):
        os.mkdir(save_file_dir)
    if msg["Type"] in [PICTURE]:
        file_name = time.strftime(
                "%Y%m%d-%H%M%S", time.localtime(msg["CreateTime"])) + msg["FileName"][msg['FileName'].rfind("."):]
    else:
        file_name = time.strftime(
            "%Y%m%d-%H%M%S", time.localtime(msg["CreateTime"])) + "+" + msg['FileName']
    file_name = file_name.replace("?", "？").replace(r"/", "-").replace(":", "：").replace(
        "*", "-").replace("<", "《").replace(">", "》").replace("|", "-").replace(",", "，")
    save_file_path = f"{save_file_dir}/{file_name}"
    if os.path.exists(save_file_path):
        log.info(f"文件已存在:{save_file_path}")
        return True
    log.info(f"开始下载文件:{save_file_path}")
    msg.download(save_file_path)
    log.info(f"下载文件成功:{save_file_path}\n")


def filter_file(msg):
    """ 筛选文件
    1. 筛入掉自己发的文件
    2. 文件大小为0的
    """
    if "NickName" not in msg["User"]:
        log.debug("自己发的文件")
        return False
    if msg["Content"] == "":
        log.debug("文件内容为空")
        return False
    if msg["ToUserName"] == msg["User"]["UserName"]:
        log.debug("3")
        return False
    return True


def filter_msg(msg):
    """ 筛选消息
    1. 非群组消息
    2. 非指定联系人
    3. 非指定关键词
    """
    global contact_list
    global keyword_list
    if "ActualNickName" not in msg:
        log.debug("非群组消息")
        return False
    elif msg["ActualNickName"] not in contact_list:
        log.debug("非指定联系人")
        return False
    elif not any(keyword in msg["Text"] for keyword in keyword_list):
        log.debug("非指定关键词")
        return False
    return True


def send_remind(msg, group_name):
    """ 发送提醒
    1. 格式
    群名: {1}
    发信人: {2}
    内容: {3}
    2. 找到指定群组发送
    """
    remind = f'群名:{msg["User"]["NickName"]}\n发信人:{msg["ActualNickName"]}\n内容:{msg["Text"]}'
    group_list = itchat.get_chatrooms()
    for g in group_list:
        if g["NickName"] == group_name:
            itchat.send_msg(remind, g["UserName"])
    log.info("发送提醒\n+" + remind + "\n")


@itchat.msg_register([TEXT, PICTURE, ATTACHMENT], isFriendChat=True, isGroupChat=True)
def reply_msg(msg):
    if msg["Type"] in [TEXT]:
        if filter_msg(msg):
            send_remind(msg, GROUP_NAME)
    elif msg["Type"] in [PICTURE, ATTACHMENT]:
        #  elif msg["Type"] in [ATTACHMENT]:
        if filter_file(msg):
            download_file(msg)


if __name__ == '__main__':
    if not os.path.exists(FILE_PATH):
        os.mkdir(FILE_PATH)
    read_config()
    itchat.auto_login(hotReload=True)
    itchat.run()
