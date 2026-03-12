import os
from datetime import datetime

from strategyBase import StrategyBase
import csv

##资金费率>0.05% 且空单爆完仓（爆仓大于1m且连续15min爆仓不增加）之后，做空，等多单爆完仓（爆仓至少涨1m，然后持续15min不增加）之后，平仓。 连续3次失败（开仓后突破止损点）停止策略，启动趋势跟随
##上涨趋势跟随：连续三次最大回撤后的价格跌破不了上一次低点，且资金费率在这三次期间持续偏高。（连续两次最大回撤跌破上一次低点/一次跌破？）趋势消失后停止策略，开启上一行策略
class Strategy1(StrategyBase):
    def __init__(self, account):
        super().__init__("Strategy1", account)
        self.logFile = "strategy1.csv"
        if not os.path.exists(self.logFile):
            with open(self.logFile, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["time", "action", "position", "value", "entryprice"])

    def onData(self, data):
        if not self.active:
            return
        else:
            #构建15min窗口
            if self.window.__len__() < 15:
                self.window.append(data)
            else:
                self.window.pop(0)
                self.window.append(data)

                if self.positions.__len__() == 0:
                    ##追加一个多头没开始爆仓的条件？
                    if  float(data["资金费率"][:-2]) > 0.005 and self.ifLiquidationEnds("short") == True :
                        newPosition = {"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": "short", "position": 0.03,
                                       "value": 0.03 * float(data["价格"][1:]), "entryprice": data["价格"] }
                        self.positions.append(newPosition)
                       # print("short action")
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                  newPosition["value"], newPosition["entryprice"])
                else:
                    self.update_pnl(data)
                    if self.ifLiquidationEnds("long") == True :
                        newPosition = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "action": "long",
                                       "position": 0.03,
                                       "value": 0.03 * float(data["价格"][1:]), "entryprice": data["价格"]}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])
                ##    if #触发止损时卖出：





    def ifLiquidationEnds(self, liqudationSide):  ##只写了爆仓逐渐减少。下一步完善成先增加后减少
        if liqudationSide == "short":
            for i in range(self.window.__len__() - 1):
                data1 = self.window[i]["Short Liquidation(1h)"]
                data2 = self.window[i + 1]["Short Liquidation(1h)"]
                print(data1.lstrip("$").rstrip("M")[:-1])
                if data1[-1] != "M" or data1.lstrip("$").rstrip("M")[:-1] < data2.lstrip("$").rstrip("M")[:-1]: ##比较爆仓数值2.1 《 2.2
                    return False
            return True
        if liqudationSide == "long":
            for i in range(self.window.__len__() - 1):
                data1 = self.window[i]["Long Liquidation(1h)"]
                data2 = self.window[i + 1]["Long Liquidation(1h)"]
                if data1[-1] != "M" or data1.lstrip("$").rstrip("M")[:-1] < data2.lstrip("$").rstrip("M")[:-1]: ##比较爆仓数值2.1 《 2.2
                    return False
            return True



