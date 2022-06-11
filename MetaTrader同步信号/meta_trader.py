import MetaTrader5 as mt5
import os
import numpy  # MetaTrader5 打包依赖
from random import randint, choice
from time import time, sleep
from lib import log, FunWrap


class MetaTraderApp:
    def __init__(self, path=None) -> None:
        self.init_var()
        self.path = path
        self.initialize(path)
        self.add_all_symbol()

    def init_var(self):
        self.account = ""
        self.price = 0.01
        self.params = {}
        self.positions = []
        self.trading_signals = None
        self.user_list = []

    def pretreatment(self, task_name=""):
        if task_name != "":
            log.info(task_name + " 开始")

    def init_user_list(self, user_list):
        if user_list.strip() == "":
            self.user_list = []
        else:
            self.user_list = user_list.split("-")

    def initialize(self, path):
        error_wait = 5
        exec_path = os.path.join(
            os.getcwd(), "MetaTraderApp", path, "terminal64.exe")
        for _ in range(3):
            #  mt5.shutdown()
            result = mt5.initialize(
                exec_path)
            #  print(exec_path,result)
            if result:
                return True
            log.error(f"initialize() failed, error code = {mt5.last_error()}")
            log.error("建立连接失败!")
            log.error(f"准备重新建立!")

    def restart_init(self):
        os.system("taskkill /f /im terminal64.exe")
        sleep(5)

    def _RawOrder(self, order_type, symbol, volume, price, comment=None, ticket=None, type_filling=None):
        order = {
            "action":    mt5.TRADE_ACTION_DEAL,
            "symbol":    symbol,
            "volume":    volume,
            "type":      order_type,
            "price":     price,
            "deviation": 10,
        }
        if comment is not None:
            order["comment"] = comment
        if ticket is not None:
            order["position"] = ticket
        #  if type_filling is not None:
            #  # mt5.ORDER_FILLING_IOC
            #  order["type_filling"] = type_filling
        order["type_filling"] = mt5.ORDER_FILLING_IOC
        return mt5.order_send(order)

    # Close all specific orders
    def Close(self, symbol, *, comment=None, ticket=None):
        if ticket is not None:
            positions = mt5.positions_get(ticket=ticket)
        else:
            positions = mt5.positions_get(symbol=symbol)
        tried = 0
        done = 0
        for pos in positions:
            # process only simple buy, sell
            if pos.type == mt5.ORDER_TYPE_BUY or pos.type == mt5.ORDER_TYPE_SELL:
                tried += 1
                for tries in range(10):
                    info = mt5.symbol_info_tick(symbol)
                    if info is None:
                        return None
                    if pos.type == mt5.ORDER_TYPE_BUY:
                        r = self._RawOrder(
                            mt5.ORDER_TYPE_SELL, symbol, pos.volume, info.bid, comment, pos.ticket)
                    else:
                        r = self._RawOrder(
                            mt5.ORDER_TYPE_BUY, symbol, pos.volume, info.ask, comment, pos.ticket)
                    # check results
                    if r is None:
                        return None
                    if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                        if r.retcode == mt5.TRADE_RETCODE_DONE:
                            done += 1
                        break
        if done > 0:
            if done == tried:
                return True
            else:
                return "Partially"
        return False

    def Buy(self, symbol, volume, price=None, *, comment=None, ticket=None):
        # with direct call
        if price is not None:
            return self._RawOrder(mt5.ORDER_TYPE_BUY, symbol, volume, price, comment, ticket)
        # no price, we try several times with current price
        r = None
        for tries in range(10):
            info = mt5.symbol_info_tick(symbol)
            r = self._RawOrder(mt5.ORDER_TYPE_BUY, symbol,
                               volume, info.ask, comment, ticket)
            if r is None:
                return None
            if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                break
        return r

    # Sell order
    def Sell(self, symbol, volume, price=None, *, comment=None, ticket=None):
        # with direct call
        if price is not None:
            return self._RawOrder(mt5.ORDER_TYPE_SELL, symbol, volume, price, comment, ticket)
        # no price, we try several times with current price
        r = None
        for tries in range(10):
            info = mt5.symbol_info_tick(symbol)
            r = self._RawOrder(mt5.ORDER_TYPE_SELL, symbol,
                               volume, info.bid, comment, ticket)
            if r is None:
                return None
            if r.retcode != mt5.TRADE_RETCODE_REQUOTE and r.retcode != mt5.TRADE_RETCODE_PRICE_OFF:
                break
        return r

    def add_all_symbol(self):
        for symbol_info in mt5.symbols_get():
            if not symbol_info.visible:
                if mt5.symbol_select(symbol_info.name, True):
                    log.info(f"添加{symbol_info.name}成功")
                else:
                    log.info(f"添加{symbol_info.name}失败")

    def get_account_info(self):
        account_info = mt5.account_info()
        log.info(f"账号:{account_info.login}")
        return account_info.login

    def order_send(self, request):
        for _ in range(3):
            result = mt5.order_send(request)
            #  print("请求结果", result.retcode)
            if result.retcode == 10009:
                return True
            elif result.retcode == 10004:
                return False
            if result.retcode == 10021:
                return False
            log.warning(f"请求失败:{result.retcode}")
        return False

    @FunWrap("买入", True)
    def buy(self, symbol, volume):
        for _ in range(3):
            result = self.Buy(symbol, volume)
            #  print(result.retcode)
            if result:
                if result.retcode != 10009:
                    log.info(result.retcode)
                    continue
                log.info(f"{symbol} 买入 {volume} 成功")
                return True
        log.warning(f"{symbol} 买入 {volume} 失败")
        return False
        for _ in range(3):
            price = mt5.symbol_info_tick(symbol)
            if price is None:
                if mt5.symbol_select(symbol, True):
                    log.info(f"{symbol}交易品种添加成功")
                else:
                    log.error(f"{symbol}交易品种添加成功")
                    return False
            price = price.ask
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
                "comment": "python script open",
            }
            result1 = mt5.order_check(request)
            if result1.retcode != 0:
                log.warning("检查订单不通过")
                log.warning(result1)
                continue
            result = self.order_send(request)
            if not result:
                continue
            log.info(f"{symbol} 买入 {volume} 成功")
            return True
        log.warning(f"{symbol} 买入 {volume} 失败")
        return False

    @FunWrap("卖出", True)
    def sell(self, symbol, volume):
        for _ in range(3):
            result = self.Sell(symbol, volume)
            #  print(result)
            if result:
                if result.retcode != 10009:
                    log.warning(result.retcode)
                    continue
                log.info(f"{symbol} 卖出 {volume} 成功")
                return True
        log.warning(f"{symbol} 卖出 {volume} 失败")
        return False
        return
        #  print(symbol,volume)
        #  return
        for _ in range(3):
            price = mt5.symbol_info_tick(symbol).bid
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": price,
                #  "comment": "python script open",
            }
            result = self.order_send(request)
            if not result:
                continue
            log.info(f"{symbol} 卖出 {volume} 成功")
            return True
        log.warning(f"{symbol} 卖出 {volume} 失败")
        return False

    @FunWrap("平仓", True)
    def close(self, symbol, position_id):
        #  print(symbol,position_id)
        #  return
        for _ in range(3):
            result = self.Close(symbol, ticket=position_id)
            #  print(result)
            if result:
                log.info(f"{position_id} 关闭成功")
                return True
            #  log.info(f"关闭失败")
        log.warning(f"{position_id} 关闭失败")
        return False

    @FunWrap("", True)
    def positions_get(self):
        positions = []
        for position in mt5.positions_get():
            positions.append({
                "order": position.ticket,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": position.type,
            })
        positions = self.set_positions_rank(positions)
        return positions

    def exit(self):
        mt5.shutdown()

    def get_diff_positions_by_one(self, positions):
        """
        获取不同的订单数
        存在相同 去掉 最后留下来的是新交易 positions
        """
        trad_positions = [position.copy() for position in positions]
        self.positions = self.positions_get()
        close_positions = []
        for i, p1 in enumerate(self.positions):
            flags = -1
            for j, p2 in enumerate(trad_positions):
                if p1["order"] != p2["order"]:
                    continue
                #  print("移除:", p2)
                trad_positions.remove(p2)
                flags = 1
                break
            if flags == -1:
                #  print("添加:", self.positions[i])
                close_positions.append(self.positions[i])
        return [trad_positions, close_positions]

    def get_diff_positions(self, positions):
        """
        获取不同的订单数
        存在相同 去掉 最后留下来的是新交易 positions
        """
        _positions = [position.copy() for position in positions]
        self.positions = self.positions_get()
        close_positions = []
        for i, p1 in enumerate(self.positions):
            flags = -1
            for j, p2 in enumerate(_positions):
                if p1["symbol"] != p2["symbol"]:
                    continue
                #  elif p1["volume"] != p2["volume"]:
                    #  continue
                elif p1["type"] != p2["type"]:
                    continue
                if p1["rank"] != p2["rank"]:
                    continue
                #  print("移除:", p2)
                _positions.remove(p2)
                flags = 1
                break
            if flags == -1:
                #  print("添加:", self.positions[i])
                close_positions.append(self.positions[i])
        return [close_positions, _positions]

    #  @FunWrap("交易操作", True)
    def single_operation(self, positions: list):
        """
        根据订单数操作
        订单数减少，平仓操作
        订单数增加，买入卖出操作
        """
        diff_positions = self.get_diff_positions(positions)
        close_positions = diff_positions[0]
        trad_positions = diff_positions[1]
        if close_positions:
            self.get_account_info()
            log.info("关闭列表")
            log.info(close_positions)
        if trad_positions:
            self.get_account_info()
            log.info("交易列表")
            log.info(trad_positions)
        for position in close_positions:
            self.close(
                position["symbol"], position["order"])
            return True
        for position in trad_positions:
            if position["type"] == 0:
                self.buy(position["symbol"], self.price)
            elif position["type"] == 1:
                self.sell(position["symbol"], self.price)
            else:
                log.warning("未知操作！！！")
            return True

    @FunWrap("监控订单", True)
    def monitor_orders(self):
        """
        订单数无变化 继续监控
        订单数变化   发送信号
        """
        if not self.user_list:
            self.get_account_info()
            log.warning("没有需要同步的用户")
            return False
        self.initialize(self.path)
        while True:
            try:
                current_positions = self.positions_get()
                sleep(0.5)
                diff_positions = self.get_diff_positions_by_one(
                    current_positions)
                if diff_positions[0]:
                    for position in diff_positions[0]:
                        current_positions.remove(position)
                if diff_positions[1]:
                    for position in diff_positions[1]:
                        current_positions.append(position)
                self.all_user_single_operation(current_positions)
            except Exception as e:
                if str(e) == "停止线程":
                    raise Exception("停止线程")
                log.exception(e)
                self.restart_init()
                self.initialize(self.path)

    def all_user_single_operation(self, positions: list):
        for path in self.user_list:
            self.initialize(path)
            #  self.get_account_info()
            self.single_operation(positions)
        self.initialize(self.path)
        self.positions = self.positions_get()

    def random_trading(self):
        #  symbol_list = ["EURUSD", "GBPUSD", "USDCHF", "USDJPY"]
        symbol_list = []
        for symbol_info in mt5.symbols_get():
            if symbol_info.visible:
                symbol_list.append(symbol_info.name)
        max_value = 30
        for _ in range(10000):
            print(f"第{_}次")
            if randint(1, max_value) in [3, 6, 9, 12, 15, 18, 21]:
                self.positions = self.positions_get()
                if not self.positions:
                    continue
                position = choice(self.positions)
                self.close(position["symbol"], position["order"])
            elif randint(1, max_value) in [1, 4, 7, 11, 13, 15]:
                self.sell(choice(symbol_list), 0.01 * randint(1, 9))
            elif randint(1, max_value) in [2, 5, 8, 10, 12, 14]:
                self.buy(choice(symbol_list), 0.01 * randint(1, 9))
            sleep(1)

    #  def set_positions_rank(self, positions):
        #  list1 = []
        #  for position in positions:
            #  for li in list1:
            #  if not li:
            #  continue
            #  if position["symbol"] in li[0]["symbol"]:
            #  li.append(position)
            #  break
            #  else:
            #  list1.append([position])
        #  list2 = []
        #  for li in list1:
            #  li.sort(key=lambda position: position["order"], reverse=False)
            #  for j, position in enumerate(li):
            #  position["rank"] = j + 1
            #  list2.append(position)
        #  return list2

    def set_positions_rank(self, positions):
        list1 = []
        for position in positions:
            for li in list1:
                if not li:
                    continue
                if position["symbol"] in li[0]["symbol"] and position["type"] == li[0]["type"]:
                    li.append(position)
                    break
            else:
                list1.append([position])
        list2 = []
        for li in list1:
            li.sort(key=lambda position: position["order"], reverse=False)
            for j, position in enumerate(li):
                position["rank"] = j + 1
                list2.append(position)
        list2.sort(key=lambda position: position["order"], reverse=False)
        #  print(list2)
        return list2

    def main(self):
        #  self.Buy("EURUSD", 0.01)
        #  self.buy("EURGBP",0.01)
        self.random_trading()
        #  self.add_all_symbol()
        #  self.monitor_orders()
        #  self.restart_init()
        #  for path in self.user_list:
        #  self.initialize(path)
        #  self.initialize(self.path)
        input("回车继续")
        return


if __name__ == "__main__":
    user1 = MetaTraderApp("M1")
    #  user1.user_list = ["fu2", "fu3"]
    user1.main()
    user1.exit()
