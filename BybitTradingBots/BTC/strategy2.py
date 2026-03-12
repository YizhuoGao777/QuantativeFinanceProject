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


        if not self.active:
            return
        else:
            if self.positions.__len__() == 0:
                if  (float(data[-1]["Hist"]) > 0 and float(data[-2]["Hist"]) < 0 ):  ####and float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) > float(data["volume"])
                    position = (20 + self.pnl) / float(data["close"])

                    newPosition = {"time":data["close_time"], "action": "long", "position": position,
                                   "value": position * float(data["close"]), "entryprice": float(data["close"]) }
                    self.positions.append(newPosition)

                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                              newPosition["value"], newPosition["entryprice"])
            else:

                if  (float(data[-1]["Hist"]) < 0 ):
                    self.update_pnl(data)
                    newPosition = {"time": data["close_time"], "action": "short",
                                   "position": self.positions[0]["position"],
                                   "value": self.positions[0]["position"] * float(data["close"]), "entryprice": float(data["close"])}

                    self.positions.pop(0)
                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                  newPosition["value"], newPosition["entryprice"])
