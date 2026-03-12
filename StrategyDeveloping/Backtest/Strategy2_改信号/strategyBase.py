import csv
class StrategyBase:
    def __init__(self, name, account):
        self.name = name
        self.account = account
        self.active = True
        self.pnl = 0
        self.window = []
        self.positions = []
        account.register_strategy(self)


    def logTrade(self, logfile,time, action, position, value, entryprice):
        with open(logfile, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([time, action, position, value, entryprice])

    def update_pnl(self, data):
        for position in self.positions:
            previousValue = position["value"]
            newValue = float(data["close"] )* position["position"]
            if position["action"] == "long":
                pnl = newValue - previousValue
                self.pnl += pnl
            if position["action"] == "short":
                pnl = previousValue - newValue
                self.pnl += pnl

    def calculate_pnl(self, data):
        pnl = 0
        for position in self.positions:
            previousValue = position["value"]
            newValue = float(data["close"] )* position["position"]
            if position["action"] == "long":
                pnl = newValue - previousValue

            if position["action"] == "short":
                pnl = previousValue - newValue
        return pnl





    def pause(self):
        self.active = False

    def resume(self):
        self.active = True
