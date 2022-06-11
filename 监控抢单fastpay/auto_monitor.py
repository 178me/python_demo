import winsound
from web_auto import WebAutoModule
from lib import FunWrap, log, Other
from time import sleep


class Fun1(WebAutoModule):
    def __init__(self, browse_name="") -> None:
        super().__init__(browse_name)
        self.init_var()

    def init_var(self):
        self.params = {}
        self.thread_status = "init"

    def pretreatment(self, task_name=""):
        pass

    def switch_iframe(self):
        iframe = self.find_elem('//*[@id="con_3"]/iframe')
        self.driver.switch_to.frame(iframe)

    @FunWrap("查找抢单按钮", True)
    def get_operate_btn(self):
        cmb_list = []
        #  elems = self.find_elems(
            #  '//td/span[@class="text-danger"]')
        elems = self.find_elems(
            '//td/a[@title="抢单"]',find_time=1)
        if not elems:
            log.warning("没有找到抢单按钮")
            return cmb_list
        try:
            for e in elems:
                cmb_list.append({
                    #  "location": self.get_center_pos(e),
                    "elem": e
                })
        except:
            log.error("获取抢单按钮失败")
        return cmb_list

    @FunWrap("获取操作按钮", True)
    def click_operate_btn(self,elem):
        self.driver.execute_script("arguments[0].click()",elem)

    @FunWrap("获取金额", True)
    def get_price(self, elem):
        try:
            elems = elem.find_element(self.By.XPATH,"//parent::*/parent::*/parent::*//td/span[@class='text-danger']")
            if not elems:
                log.warning("没有找到金额")
                return False
            return elems.get_attribute("textContent").strip()
        except:
            return False

    def refresh_web(self):
        self.find_elem('//button[@type="submit"]',is_click=True)

    def beep(self):
        winsound.Beep(3000, 5000)

    """ --------------------------------------------------------------------- """

    def main(self):
        log.debug("测试")
        print(self.driver.title)
        self.switch_iframe()
        btn_list = self.get_operate_btn()
        #  print(self.get_price(btn_list[0]["elem"]))
        self.refresh_web()


if __name__ == "__main__":
    log.debug("功能测试")
    xp = Fun1("Chrome")
    xp.main()
