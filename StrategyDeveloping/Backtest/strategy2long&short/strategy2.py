import os
from datetime import datetime

from strategyBase import StrategyBase
import csv



class Strategy1(StrategyBase):
    def __init__(self, account):
        super().__init__("Strategy2", account)
        self.logFile = "strategy2.csv"
        self.positionMaxPnl = 0.0
        if not os.path.exists(self.logFile):
            with open(self.logFile, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["time", "action", "position", "value", "entryprice"])

    def onData(self, data):
        data1 = data[0]
        data2 = data[1]

        if not self.active:
            return
        else:
            #构建窗口
            if self.window.__len__() < 3:
                self.window.append(data1)
            else:
                self.window.pop(0)
                self.window.append(data1)

                if self.positions.__len__() == 0:

                    if  float(data1["Hist"]) > 0 and float(self.window[-2]["Hist"]) < 0  and float(data2["Hist"]) > 0 :  ####and not (float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) < float(data["volume"]))
                        position = (100 + self.pnl) / float(data1["close"])
                        newPosition = {"time":data1["close_time"], "action": "long", "position": position,
                                       "value": position * float(data1["close"]), "entryprice": float(data1["close"])}
                        self.positions.append(newPosition)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                    if float(data1["Hist"]) < 0 and float(self.window[-2]["Hist"]) > 0 and float(data2["Hist"]) < 0:
                        position = (100 + self.pnl) / float(data1["close"])
                        newPosition = {"time": data1["close_time"], "action": "short", "position": position,
                                       "value": position * float(data1["close"]), "entryprice": float(data1["close"])}
                        self.positions.append(newPosition)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])
                else:###已经持仓时
                    if self.positions[-1]["action"] == "long" and float(data1["Hist"] )< 0 or float(data1["close"])/float(self.window[-2]["close"]) < 0.7: ##0.7,1.3
                        ###平已有duo仓
                        self.update_pnl(data1)
                        newPosition = {"time": data1["close_time"], "action": "short",
                                       "position": self.positions[0]["position"],
                                       "value": self.positions[0]["position"] * float(data1["close"]),
                                       "entryprice": float(data1["close"])}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                    elif self.positions[-1]["action"] == "short" and float(data1["Hist"]) > 0 or float(data1["close"])/float(self.window[-2]["close"]) > 1.3:

                            ###平已有空仓
                            self.update_pnl(data1)
                            newPosition = {"time": data1["close_time"], "action": "long",
                                           "position": self.positions[0]["position"],
                                           "value": self.positions[0]["position"] * float(data1["close"]),
                                           "entryprice": float(data1["close"])}

                            self.positions.pop(0)
                            self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                          newPosition["value"], newPosition["entryprice"])


