import re
from web_auto import WebAutoModule
from lib import FunWrap, log, sleep


class XuanPin(WebAutoModule):
    def __init__(self) -> None:
        super().__init__()

    def pretreatment(self, task_name=""):
        pass

    def get_number(self, temp_str):
        return int("".join(list(filter(str.isdigit, temp_str))))

    @FunWrap("获取同款商品ID", True)
    def get_same_item_id(self, same_item_url):
        #  self.open_url(same_item_url, 3)
        elems = self.find_elems(
            '//div[@class="layui-tab-item t1 layui-show"]//td[@class="lxSimilarSale"]')
        if not elems:
            return
        # 通过天猫图片的父节点找到id
        #  timao_list = self.find_elems(
            #  '//*[@class="layui-tab-item t1 layui-show"]//*[@class="lxSimilarShop"]/img/parent::*/input',find_time=0.1)
        # 通过天猫图片后面的同级节点找到id
        timao_list = self.find_elems(
            '//div[@class="layui-tab-item t1 layui-show"]//td[@class="lxSimilarShop"]/img/following-sibling::input', find_time=0.1)
        timao_nid_list = []
        for e in timao_list:
            timao_nid_list.append(e.get_attribute("nid"))
        #  return

        def sort_a(e):
            return self.get_number(e.get_attribute("textContent"))
        elems.sort(key=sort_a, reverse=True)
        nid_list = []
        for e in elems:
            if self.get_number(e.get_attribute("textContent")) < 10:
                break
            parse_elem = self.driver.execute_script(
                "return arguments[0].parentNode", e)
            nid = parse_elem.get_attribute("nid")
            if nid in timao_nid_list:
                continue
            nid_list.append(nid)
        print(nid_list)
        return nid_list

    @FunWrap("获取店铺链接", True)
    def get_store_link(self):
        elem = self.find_elem(
            '//a[@data-spm="d21"]')
        if not elem:
            return
        return elem.get_attribute("href")

    @FunWrap("获取店铺宝贝数量", True)
    def get_store_item_count(self,store_link):
        self.open_url(store_link + "search.htm?orderType=hotsell_desc")
        elem = self.find_elem(
            '//div[@class="search-result"]/span')
        if not elem:
            print("失败")
            return
        return int(elem.get_attribute("textContent"))

    @FunWrap("获取宝贝上架时间", True)
    def get_item_start_date(self,item_link):
        #  self.open_url(item_link + "search.htm?orderType=hotsell_desc")
        elem = self.find_elem(
            '//span[@class="eachItem shangjiaTime second"]/span')
        if not elem:
            print("失败")
            return
        print(elem.get_attribute("textContent"))
        return elem.get_attribute("textContent")

    @FunWrap("获取店铺销量排行的宝贝", True)
    def get_store_hottell_item(self):
        elems = self.find_elems(
            '//span[@class="sale-num"]')
        if not elems:
            print("失败")
            return
        hotsell_list = []
        for e in elems:
            hotsell_list.append(int(re.sub(r"\D","",e.get_attribute("textContent"))))
            print(re.sub(r"\D","",e.get_attribute("textContent")))
        return hotsell_list

    @FunWrap("获取店铺新品排行的宝贝", True)
    def get_store_new_item(self):
        elems = self.find_elems(
            '//a[@class="item-name J_TGoldData"]')
        if not elems:
            print("失败")
            return False
        item_link_list = []
        for e in elems:
            item_link_list.append(e.get_attribute("href"))
        return item_link_list


    def main(self):
        #  self.get_same_item_id(
            #  "https://item.taobao.com/item.htm?spm=a230r.1.14.22.f1a81389bpUShl&id=641341517310")
        #  self.get_store_link()
        #  self.get_store_item_count("https://shop277088919.taobao.com/")
        #  self.get_store_hottell_item()
        #  self.get_store_new_item()
        self.get_item_start_date("")


if __name__ == "__main__":
    print("网页模块测试")
    xp = XuanPin()
    xp.main()
