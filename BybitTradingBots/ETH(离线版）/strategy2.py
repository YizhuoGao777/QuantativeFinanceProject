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
            with open(self.logFile, mode="w", newline="", encoding="utf-8", ) as f:
                writer = csv.writer(f)
                writer.writerow(["time", "action", "position", "value", "entryprice"])

    def onData(self, data):
        k1h = data[0]  ##最新的3条1hk线
        k4h = data[1]



        if self.positions.__len__() == 0:
            if  (float(k1h[-1]["Hist"]) > 0 and float(k1h[-2]["Hist"]) < 0) and float(k4h[-1]["Hist"]) > 0 :  ####and not (float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) < float(data["volume"]))
                position = (200 + self.pnl) / float(k1h[-1]["close"])
                newPosition = {"time":k1h[-1]["close_time"], "action": "long", "position": position,
                               "value": position * float(k1h[-1]["close"]), "entryprice": float(k1h[-1]["close"])}
                self.positions.append(newPosition)
                self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                          newPosition["value"], newPosition["entryprice"])
                print(newPosition)
        else:
            if  (float(k1h[-1]["Hist"]) < 0) or float(k1h[-1]["close"])/float(k1h[-1]["close"]) < 0.95 :
                self.update_pnl(k1h[-1])
                newPosition = {"time": k1h[-1]["close_time"], "action": "short",
                               "position": self.positions[0]["position"],
                               "value": self.positions[0]["position"] * float(k1h[-1]["close"]), "entryprice": float(k1h[-1]["close"])}
                self.positions.pop(0)
                self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                              newPosition["value"], newPosition["entryprice"])
                print(newPosition)