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
                self.window.append(data)
            else:
                self.window.pop(0)
                self.window.append(data)

                if self.positions.__len__() == 0:
                    if (float(data2["MAVOL7"]) * 3 < float(data2['volume']) and float(data2['open']) - float(data2['close']) < 0 and data2 != self.window[-2][1]):  ####and not (float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) < float(data["volume"]))
                        position = (200 + self.pnl) / float(data2["close"])

                        newPosition = {"time": data2["close_time"], "action": "long", "position": position,
                                       "value": position * float(data2["close"]), "entryprice": float(data2["close"])}
                        self.positions.append(newPosition)

                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                    if (float(data2["MAVOL7"]) * 3 < float(data2['volume']) and float(data2['open']) - float(data2['close']) > 0 and data2 != self.window[-2][1]):
                        position = (200 + self.pnl) / float(data2["close"])

                        newPosition = {"time": data2["close_time"], "action": "short", "position": position,
                                       "value": position * float(data2["close"]), "entryprice": float(data2["close"])}
                        self.positions.append(newPosition)

                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                else:
                    ###交易所平duo仓

                    if (self.positions[-1]["action"] == "long" and float(data2["open"]) - float(data2['close']) > 0
                            and float(data2['volume']) > float(data2['MAVOL7'])
                            and float(data2['volume']) > float(data2['MAVOL14'])):

                        self.update_pnl(data2)
                        newPosition = {"time": data2["close_time"], "action": "short",
                                       "position": self.positions[0]["position"],
                                       "value": self.positions[0]["position"] * float(data2["close"]),
                                       "entryprice": float(data2["close"])}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                    elif (self.positions[-1]["action"] == "long" and float(self.positions[-1]["entryprice"]) / float(data1["close"]) > 1.05):
                        self.update_pnl(data1)
                        newPosition = {"time": data1["close_time"], "action": "short",
                                       "position": self.positions[0]["position"],
                                       "value": self.positions[0]["position"] * float(data1["close"]),
                                       "entryprice": float(data1["close"])}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])

                    #####平空仓

                    elif (self.positions[-1]["action"] == "short" and float(data2["open"]) - float(data2['close']) < 0
                          and float(data2['volume']) > float(data2['MAVOL7'])
                          and float(data2['volume']) > float(data2['MAVOL14'])):
                        ###

                        self.update_pnl(data2)
                        newPosition = {"time": data2["close_time"], "action": "long",
                                       "position": self.positions[0]["position"],
                                       "value": self.positions[0]["position"] * float(data2["close"]),
                                       "entryprice": float(data2["close"])}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])
                    elif (self.positions[-1]["action"] == "short" and float(self.positions[-1]["entryprice"]) / float(data1["close"]) < 0.95):
                        self.update_pnl(data1)
                        newPosition = {"time": data1["close_time"], "action": "long",
                                       "position": self.positions[0]["position"],
                                       "value": self.positions[0]["position"] * float(data1["close"]),
                                       "entryprice": float(data1["close"])}

                        self.positions.pop(0)
                        self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                      newPosition["value"], newPosition["entryprice"])