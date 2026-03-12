class Account:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.strategies = []

    def register_strategy(self, strategy):
        self.strategies.append(strategy)


    def total_pnl(self):
        return sum(s.pnl for s in self.strategies)

    def total_equity(self):
        return self.cash

    def showStatus(self):
        print(f"\n💼 总资金：{self.cash:.2f}，总收益：{self.total_pnl():.2f}")
        for name, info in self.strategies.items():
            status = "✅启用" if info["active"] else "⏸️停用"
            print(f" - {name}: 收益 {info['pnl']:.2f}，状态 {status}")
