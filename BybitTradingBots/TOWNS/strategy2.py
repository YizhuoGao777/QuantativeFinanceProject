import os
from datetime import datetime

from strategyBase import StrategyBase
import csv



class Strategy1(StrategyBase):
    def __init__(self, account):
        super().__init__("Strategy2", account)
        self.logFile = "CAKElog2025.10.csv"
        self.positionMaxPnl = 0.0
        if not os.path.exists(self.logFile):
            with open(self.logFile, mode="a", newline="", encoding="utf-8", ) as f:
                writer = csv.writer(f)
                writer.writerow(["time", "action", "position", "value", "entryprice"])

    def onData(self, data):
        k1h = data[0]  ##最新的3条1hk线
        k4h = data[1]



        if self.positions.__len__() == 0:
            if  (float(k1h[-1]["MACD"]) > float(k1h[-2]["MACD"]) ) and float(k4h[-1][0]["MACD"]) > float(k4h[-1][1]["MACD"]) :####and not (float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) < float(data["volume"]))
                amount = float(self.session.get_transferable_amount(coinName="USDT")['result']['availableWithdrawal']) #####90%资金开仓

                position = round((amount*0.3) / float(k1h[-1]["close"]), 0)
                ######交易所开duo仓
                order = self.session.place_order(
                    category="linear",
                    symbol="TOWNSUSDT",
                    side="Buy",
                    orderType="Market",
                    qty=str(position),
                    isLeverage=0,
                    orderFilter="Order",
                    stopLoss =str(float(k1h[-1]["close"])* 0.7),
                )

                print(order['retMsg'] + 'time' + str(order['time']))

                if order['retMsg'] == "OK":
                    newPosition = {"time":k1h[-1]["close_time"], "action": "long", "position": position,
                                   "value": position * float(k1h[-1]["close"]), "entryprice": float(k1h[-1]["close"])}
                    self.positions.append(newPosition)
                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                              newPosition["value"], newPosition["entryprice"])
                    print(newPosition)

            if (float(k1h[-1]["MACD"]) < float(k1h[-2]["MACD"]) ) and float(k4h[-1][0]["MACD"]) < float(k4h[-1][1]["MACD"]):  ####and not (float(data["close"]) < float(data["open"]) and float(self.window[-2]["volume"]) < float(data["volume"]))
                amount = float(self.session.get_transferable_amount(coinName="USDT")['result']['availableWithdrawal'])  #####90%资金开仓
                position = round((amount * 0.3) / float(k1h[-1]["close"]), 0)
                ######交易所开kong仓
                order = self.session.place_order(
                    category="linear",
                    symbol="TOWNSUSDT",
                    side="Sell",
                    orderType="Market",
                    qty=str(position),
                    isLeverage=0,
                    orderFilter="Order",
                    stopLoss=str(float(k1h[-1]["close"]) * 1.3),
                )
                print(order['retMsg'] + 'time' + str(order['time']))
                if order['retMsg'] == "OK":
                    newPosition = {"time": k1h[-1]["close_time"], "action": "short", "position": position,
                                   "value": position * float(k1h[-1]["close"]),
                                   "entryprice": float(k1h[-1]["close"])}
                    self.positions.append(newPosition)
                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                  newPosition["value"], newPosition["entryprice"])
                    print(newPosition)
        else:
            if self.positions[-1]["action"] == "long" and (float(k1h[-1]["MACD"]) < float(k1h[-2]["MACD"])):
                ###交易所平duo仓
                order = self.session.place_order(
                    category="linear",
                    symbol="TOWNSUSDT",
                    side="Sell",
                    orderType="Market",
                    qty=str(self.positions[0]["position"]),
                    isLeverage=0,
                    orderFilter="Order",
                )

                print(order['retMsg'] + 'time' + str(order['time']))

                if order['retMsg'] == "OK":
                    self.update_pnl(k1h[-1])
                    newPosition = {"time": k1h[-1]["close_time"], "action": "short",
                                   "position": self.positions[0]["position"],
                                   "value": self.positions[0]["position"] * float(k1h[-1]["close"]), "entryprice": float(k1h[-1]["close"])}
                    self.positions.pop(0)
                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                  newPosition["value"], newPosition["entryprice"])
                    print(newPosition)

            elif self.positions[-1]["action"] == "short" and (float(k1h[-1]["MACD"]) > float(k1h[-2]["MACD"])):
                ###交易所平kong仓
                order = self.session.place_order(
                    category="linear",
                    symbol="TOWNSUSDT",
                    side="Buy",
                    orderType="Market",
                    qty=str(self.positions[0]["position"]),
                    isLeverage=0,
                    orderFilter="Order",
                )

                print(order['retMsg'] + 'time' + str(order['time']))

                if order['retMsg'] == "OK":
                    self.update_pnl(k1h[-1])
                    newPosition = {"time": k1h[-1]["close_time"], "action": "long",
                                   "position": self.positions[0]["position"],
                                   "value": self.positions[0]["position"] * float(k1h[-1]["close"]), "entryprice": float(k1h[-1]["close"])}
                    self.positions.pop(0)
                    self.logTrade(self.logFile, newPosition["time"], newPosition["action"], newPosition["position"],
                                  newPosition["value"], newPosition["entryprice"])
                    print(newPosition)
