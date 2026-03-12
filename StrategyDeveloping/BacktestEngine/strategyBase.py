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
            if position["action"] == "long":
                self.pnl += float(data["价格"][1:]) * position["position"] - position["value"]
            if position["action"] == "short":
                self.pnl += position["value"] - float(data["价格"][1:]) * position["position"]




    def pause(self):
        self.active = False

    def resume(self):
        self.active = True
