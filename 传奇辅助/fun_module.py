import time
from random import randint
from auto_moudle import AutoMationModule
from lib import FunWrap, log, sleep


class ChuanQi(AutoMationModule):
    def __init__(self):
        # 初始化父类方法
        super(ChuanQi, self).__init__()
        #  self.jgy = JianGuoYun("1403341393@qq.com", "abhdwrkfxxrnhnyf")
        self.set_script_message = None
        # 显示脚本状态的信号
        self.init_var()

    def init_var(self):
        # 脚本执行状态
        self.status = "初始化"
        # 执行参数
        self.params = {}
        self.date = time.strftime("%m-%d", time.localtime())
        # 自定义参数----
        self.one_task_list = [
            {
                "task_name": self.sign_in,
                "is_finish": False
            },
            {
                "task_name": self.list_worship,
                "is_finish": False
            },
            {
                "task_name": self.lian_sha_qi_yu,
                "is_finish": False
            },
            {
                "task_name": self.my_boss,
                "is_finish": False
            }
        ]
        self.many_task_list = [
            {
                "task_name": self.online_rewards,
                "is_finish": False
            },
            # {
            #     "task_name": self.yun_biao,
            #     "is_finish": False
            # },
            # {
            #     "task_name": self.kuang_dong,
            #     "is_finish": False
            # },
            {
                "task_name": self.pk,
                "is_finish": False
            },
            {
                "task_name": self.tian_ti,
                "is_finish": False
            },
            {
                "task_name": self.cai_liao_fu_ben,
                "is_finish": False
            },
            {
                "task_name": self.get_rewards,
                "is_finish": False
            },
        ]
        self.point_list = [
            {
                "name": "背包",
                "point": (300, 850),
            },
            {
                "name": "福利",
                "point": (130, 220),
            },
            {
                "name": "排行榜",
                "point": (40, 600),
            },
            {
                "name": "竞技",
                "point": (950, 480),
            },
            {
                "name": "副本",
                "point": (950, 540),
            },
            {
                "name": "领主",
                "point": (950, 580),
            },
            {
                "name": "日常",
                "point": (950, 440),
            },
            # -----------------------
            {
                "name": "上一页",
                "point": (280, 780),
            },
            {
                "name": "下一页",
                "point": (640, 780),
            },
            {
                "name": "在线奖励",
                "point": (450, 780),
            },
            {
                "name": "签到",
                "point": (470, 780),
            },
            {
                "name": "pk",
                "point": (360, 780),
            },
            {
                "name": "运镖",
                "point": (500, 780),
            },
            {
                "name": "跨服天梯",
                "point": (560, 780),
            },
            {
                "name": "矿洞",
                "point": (460, 780),
            },
            {
                "name": "连杀奇遇",
                "point": (530, 780),
            },
            {
                "name": "个人Boss",
                "point": (360, 780),
            },
            {
                "name": "任务",
                "point": (580, 780),
            },
        ]

    def pretreatment(self, task_name=""):
        ''' 预处理函数(每个函数开始之前执行) '''
        if "stop" in self.status:
            self.exit()
            self.set_status("停止脚本")
            self.dl("停止线程")
            raise Exception("停止线程")
        if task_name != "":
            self.dl(task_name + " 开始")
            self.set_status(task_name)

    def set_status(self, status_text):
        ''' 设置脚本状态 '''
        self.status = status_text
        if self.set_script_message:
            self.set_script_message.emit(self.index, status_text)

    @FunWrap("设置固定窗口", True)
    def set_fix_window(self):
        self.dll.setWindowSize(self.hwnd, 1001, 892)

    @FunWrap("", True)
    def than_date(self):
        date = time.strftime("%m-%d", time.localtime())
        if self.date == date:
            return True
        self.date = date
        return False

    @FunWrap("", True)
    def wait(self,sec):
        count = sec
        for _ in range(count):
            self.wait(1)
            sec -= 1
            self.set_status(f"挂机中:{sec}秒")

    @FunWrap("", True)
    def previous_page(self):
        self.click_map("上一页")
        return True

    @FunWrap("", True)
    def next_page(self):
        self.click_map("下一页")
        return True

    @FunWrap("", True)
    def close(self, count=1):
        for _ in range(count):
            self.find_image_by_dll(
                "关闭.bmp", is_click=True, find_time=0.1, sim=0.9)

    @FunWrap("", True)
    def back_main_page(self):
        result = self.find_image_by_dll(
            "日常.bmp", is_click=False, find_time=1, sim=0.9)
        if result:
            return True
        self.close(5)

    @FunWrap("", True)
    def click_map(self, point_name,**option):
        for value in self.point_list:
            if value["name"] == point_name:
                x, y = value["point"]
        self.click(x,y,**option)

    @FunWrap("", True)
    def jump_to(self, point_name, count=3):
        self.back_main_page()
        result, x, y = None, None, None
        for value in self.point_list:
            if value["name"] == point_name:
                x, y = value["point"]
        if not x:
            self.dl(f"跳转{point_name}失败!")
            return False
        for _ in range(count):
            self.click(x, y)
            result = self.find_image_by_dll(
                "关闭.bmp", find_time=1, sim=0.9)
            if result:
                break
        sleep(0.5)
        return result

    @FunWrap("等待战斗完成", True)
    def wait_fight_finish(self):
        for _ in range(120):
            result = self.find_image_by_dll(
                "关闭.bmp|日常.bmp", is_click=False, find_time=1, sim=0.8)
            # self.dl(result)
            if result:
                break

    @FunWrap("自动熔炼", True)
    def auto_recycl(self):
        result = self.jump_to("背包")
        if not result:
            self.dl("自动熔炼失败:未找到背包")
            return False
        result = self.find_image_by_dll(
            "熔炼入口.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("自动熔炼失败:未找到熔炼入口")
            return False
        for _ in range(3):
            self.find_image_by_dll(
                "熔炼.bmp", is_click=True, find_time=0.5, sim=0.9)
        self.close(5)
        return True

    @FunWrap("签到", True)
    def sign_in(self):
        self.jump_to("福利")
        self.click_map("签到")
        result = self.find_images_by_dll(
            "已签到.bmp", find_time=1, sim=0.6)
        if not result:
            self.dl("未进入到签到页面")
            return False
        result_list = []
        for i in range(2):
            for _ in range(3):
                result = self.find_images_by_dll(
                    "已签到.bmp", find_time=1, sim=0.55)
                result_list.append(len(result))
                sleep(0.5)
            day = max(result_list)
            # print(result_list)
            if day < 20:
                break
            result_list = []
            self.drag(500,700,500,200,1)
            sleep(1)
        start_x,start_y,width,height = 319,413,80,100
        x = start_x + ((day % 5) * width)
        y = start_y + ((int(day / 5)) * height)
        self.click(x,y)
        self.dl(f"领取第{day + 1}天的奖励")
        self.one_task_list[0]["is_finish"] = True

    @FunWrap("在线奖励", True)
    def online_rewards(self):
        self.jump_to("福利")
        self.previous_page()
        self.click(660,780)
        self.click_map("在线奖励")
        for _ in range(4):
            result = self.find_image_by_dll(
                "领取.bmp", is_click=True, find_time=0.5, sim=0.8, direction=3)
            if not result:
                break
            sleep(1)
        #  result = self.find_image_by_dll(
            #  "在线1小时.bmp", is_click=True, find_time=0.5, sim=0.8, direction=0)
        #  if result:
            #  self.dl("在线1小时")
            #  self.many_task_list[0]["is_finish"] = True

    @FunWrap("排行榜膜拜", True)
    def list_worship(self):
        self.jump_to("排行榜")
        # 第一个榜的中心
        offset_x, offset_y = 650, 460
        self.drag(offset_x, offset_y, offset_x, offset_y+100, 0.5)
        for i in range(9):
            self.click(offset_x, offset_y)
            self.click(650,410)
            if i == 6:
                self.drag(offset_x, offset_y, offset_x, 300, 0.5)
                sleep(1)
            else:
                # 加上按钮高度
                offset_y += 40
        self.one_task_list[1]["is_finish"] = True

    @FunWrap("PK", True)
    def pk(self):
        self.jump_to("竞技")
        self.previous_page()
        self.click_map("pk", click_delay=0.5)
        self.click(570, 420)
        self.is_disappear_by_image("关闭.bmp",15,3)
        self.wait_fight_finish()
        result = self.find_image_by_dll(
            "开启.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("没有秘宝可开启!")
            return False
        result = self.find_image_by_dll(
            "领取秘宝.bmp", is_click=True, find_time=3, sim=0.9)
        if not result:
            self.dl("开启秘宝失败!")
            return False
        return True

    @FunWrap("运镖", True)
    def yun_biao(self):
        self.jump_to("竞技")
        self.previous_page()
        self.click_map("运镖", click_delay=0.5)
        result = self.find_image_by_dll(
            "运镖次数0.bmp", is_click=True, find_time=0.5, sim=0.9, direction=0)
        if result:
            self.dl("次数不足!")
            self.many_task_list[1]["is_finish"] = True
            return False
        result = self.find_image_by_dll(
            "开始运镖.bmp", is_click=True, find_time=1, sim=0.8)
        if not result:
            self.dl("正在运镖中!")
            return False
        result = self.find_image_by_dll(
            "提升品质.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("提升品质失败!")
        result = self.find_image_by_dll(
            "护送.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("护送失败!")
            return False
        result = self.find_image_by_dll(
            "确定.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("护送失败!")
            return False
        return True

    @FunWrap("跨服天梯", True)
    def tian_ti(self):
        self.jump_to("竞技")
        self.previous_page()
        self.click_map("跨服天梯", click_delay=0.5)
        result = self.find_image_by_dll(
            "天梯次数0.bmp", is_click=True, find_time=0.5, sim=0.9, direction=0)
        if result:
            self.dl("次数不足!")
            self.many_task_list[4]["is_finish"] = True
            return False
        result = self.find_image_by_dll(
            "挑战.bmp", is_click=True, find_time=1, sim=0.9, direction=0)
        if not result:
            self.dl("挑战失败!")
            return False
        result = self.find_image_by_dll(
            "确定挑战.bmp", is_click=True,click_delay=5, find_time=1, sim=0.9)
        if not result:
            self.dl("确定挑战失败!")
            return False
        self.wait_fight_finish()

    @FunWrap("矿洞", True)
    def kuang_dong(self):
        self.jump_to("竞技")
        self.next_page()
        self.click_map("矿洞", click_delay=0.5)
        result = self.find_image_by_dll(
            "矿洞次数0.bmp", is_click=True, find_time=0.5, sim=0.9, direction=0)
        if result:
            self.dl("次数不足!")
            self.many_task_list[2]["is_finish"] = True
            return False
        result = self.find_image_by_dll(
            "开采矿源.bmp|快速完成.bmp", is_click=False, find_time=1, sim=0.9, direction=0)
        if not result:
            self.dl("开启矿源失败!")
            return False
        if result["index"] == 1:
            self.dl("开启矿源中!")
            return False
        self.click_center(result)
        result = self.find_image_by_dll(
           "提升品质.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
           self.dl("提升品质失败!")
        result = self.find_image_by_dll(
            "雇佣开采.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("雇佣开采失败!")
            return False
        result = self.find_image_by_dll(
            "确定.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("护送失败!")
            return False
        return True

    @FunWrap("连杀奇遇", True)
    def lian_sha_qi_yu(self):
        self.jump_to("竞技")
        self.next_page()
        self.click_map('连杀奇遇', click_delay=0.5)
        result = self.find_image_by_dll(
            "次数0.bmp", is_click=False, find_time=1, sim=0.9)
        if result:
            self.dl("连杀奇遇次数不足!")
            self.one_task_list[2]["is_finish"] = True
            return False
        result = self.find_image_by_dll(
            "进入.bmp|继续挑战.bmp", is_click=True, find_time=0.5, sim=0.9)
        if not result:
            self.dl("进入连杀奇遇失败!")
            return False
        if result["index"] == 0:
            result = self.find_image_by_dll(
                "确定.bmp", is_click=True, find_time=1, sim=0.9)
            if not result:
                self.dl("开启连杀奇遇失败!")
                return False
        sleep(5)
        for _ in range(10):
            self.wait_fight_finish()
            result = self.find_image_by_dll(
                "继续挑战.bmp", is_click=True, find_time=1, sim=0.9)
            if not result:
                self.dl("继续挑战失败!")
                return False
            sleep(5)
        self.one_task_list[2]["is_finish"] = True

    @FunWrap("材料副本", True)
    def cai_liao_fu_ben(self):
        self.jump_to("副本")
        self.click(433,537)
        result = self.find_image_by_dll(
            "挑战材料副本.bmp", is_click=True, find_time=1, sim=0.9)
        if not result:
            self.dl("挑战材料副本失败!")
            return False
        self.wait_fight_finish()
        return True

    @FunWrap("个人Boss", True)
    def my_boss(self):
        self.jump_to("领主")
        self.click_map("个人Boss")
        for _ in range(30):
            result = self.find_image_by_dll(
                "挑战.bmp", y1=590, is_click=True, click_delay=3, find_time=0.5, sim=0.7, direction=0)
            if not result:
                break
            self.wait_fight_finish()
        self.one_task_list[3]["is_finish"] = True

    @FunWrap("领取奖励", True)
    def get_rewards(self):
        self.jump_to("日常")
        self.click_map("任务")
        for _ in range(30):
            result = self.find_image_by_dll(
                "点击领取奖励.bmp", is_click=True, find_time=1, sim=0.7)
            if not result:
                break
        return True

    def auto_recycl_timer(self):
        for _ in range(2):
            self.auto_recycl()
            self.wait(randint(60,120))

    @FunWrap("测试", True)
    def test(self, params):
        self.dl(params)
        self.index = int(params.get("index", 0))
        self.hwnd = int(params.get("hwnd", 0))
        self.bind_window()
        self.set_fix_window()
        # self.save_errpage()
        self.online_rewards()
        # self.tian_ti()
        #  self.wait_fight_finish()
        self.exit()
        self.set_status("脚本完成")

    def main(self, params):
        self.init_var()
        self.params = params
        self.dl(params)
        # 初始化模拟器编号和窗口句柄
        self.index = int(params.get("index", 0))
        self.hwnd = int(params.get("hwnd", 0))
        # 绑定窗口
        self.bind_window()
        try:
            self.set_fix_window()
            while True:
                self.auto_recycl()
                one_task_result = []
                for task in self.one_task_list:
                    if not task["is_finish"]:
                        task["task_name"]()
                        self.close()
                    one_task_result.append(task["is_finish"])
                self.dl(one_task_result)
                if False in one_task_result:
                    continue
                while True:
                    if not self.than_date():
                        self.dl("新的一天!")
                        self.init_var()
                        break
                    for task in self.many_task_list:
                        if not task["is_finish"]:
                            task["task_name"]()
                            self.close()
                    self.dl([task["is_finish"] for task in self.many_task_list])
                    self.auto_recycl_timer()

        except Exception as e:
            log.exception(e)
        # 功能执行结束
        self.exit()
        log.info("脚本完成")

    def show_title(self):
        if self.foobar_hwnd != 0:
            return True
        self.foobar_hwnd = self.dll.CreateFoobarRect(
            self.hwnd, 0, 0, 35, 25)
        result = self.dll.FoobarDrawText(
            self.foobar_hwnd, 0, 5, 50, 50, f" {self.index}号", "000000", 1)
        self.dll.FoobarLock(self.foobar_hwnd)
        self.dll.FoobarUpdate(self.foobar_hwnd)
        self.dl(result)


if __name__ == "__main__":
    print("自动化测试")
    qq_login = ChuanQi()
    qq_login.test({
        "index": 0,
        "hwnd": 4523326,
    })
