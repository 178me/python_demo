try:
    import os
    import sys
    if __name__ == "__main__":
        sys.path.append(os.path.abspath("./"))
except:
    "防止格式化"
    import os
import json
from time import time, sleep
from funwarp import FunWrap


class AutojsPlug:
    def __init__(self, obj):
        """ 初始化autojs数据 """
        self.autojs_plug_status = False
        self.obj = obj
        self.dl = self.obj.dl
        self.pretreatment = self.obj.pretreatment
        self.listener_path = "/sdcard/zhongkong"
        self.obj.ld.ld_base_command(
            f"echo {self.obj.index} > /sdcard/mnq_number.txt", self.obj.index, timeout=1)
        self.config_path = os.path.join(os.path.expanduser(
            '~'), "Documents", "leidian", "Pictures", f"run_fun{self.obj.index}.json")

    def open_autojs_plug(self):
        page = self.obj.find_image_by_dll(
            "插件.bmp", y1=184, y2=230, x2=20, find_time=1, sim=0.9)
        if page:
            return True
        self.obj.ld.kill_app(self.obj.index, "com.ld.autojs")
        self.obj.ld.run_app(self.obj.index, "com.ld.autojs")
        for i in range(1, 15):
            page = self.obj.find_image_by_dll(
                "插件.bmp", y1=184, y2=230, x2=20, find_time=1, sim=0.9)
            self.obj.set_table_info(f"启动中控插件:{i}秒")
            if not page:
                continue
            return True
        return False

    @FunWrap("", False)
    def base_command(self, fun_name, fun_args, exec_time=3):
        config = {
            "fun_name": fun_name,
            "fun_args": fun_args
        }
        # 写入配置
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f)
        self.obj.ld.action(self.obj.index, "call.keyboard", "menu")
        timeout = time() + exec_time
        while timeout > time():
            self.obj.pretreatment()
            result = self.obj.ld.ld_base_command(
                f'cat {self.listener_path}/run_fun.json', self.obj.index)
            if result == "":
                self.obj.dl("结果为空")
                continue
            result = json.loads(result)
            self.obj.dl(result)
            if result["fun_name"] == "已返回":
                sleep(0.1)
                result = self.obj.ld.ld_base_command(
                    f'cat {self.listener_path}/result.json', self.obj.index)
                result = json.loads(result)
                return result["result"]
        self.plug_status = self.open_autojs_plug()
        return None

    @FunWrap("", False)
    def autojs_eval(self, script_text: str, **kw):
        """ autojs插件(eval功能) """
        return self.base_command("执行脚本", {
            "script_text": script_text
        }, **kw)

    @FunWrap("", False)
    def autojs_find_node(self, seletor: str, clickable=False, **kw):
        """ autojs插件(获取节点功能) """
        return self.base_command("获取节点", {
            "selector": seletor,
            "clickable": clickable
        }, **kw)

    @FunWrap("", False)
    def autojs_find_all_node(self, seletor: str, **kw):
        """ autojs插件(获取所有节点功能) """
        return self.base_command("获取所有节点", {
            "selector": seletor
        }, **kw)
