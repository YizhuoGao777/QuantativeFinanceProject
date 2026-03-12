import csv
from datetime import datetime

from rich.live import Live
from rich.table import Table
from rich.console import Console
from account import Account
from strategy1 import Strategy1

console = Console()

# 初始化资金账户
account = Account(1000)

Strategy1(account)

# 策略收益快照，用于动态展示

def makeTable(row):
    table = Table(title="\U0001F4CA 模拟盘收益动态看板" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), expand=True)
    table.add_column("策略名称", justify="left", style="cyan")
    table.add_column("当前持仓收益", justify="right", style="green")
    table.add_column("收益率", justify="right", style="yellow")

    totalPnl = account.total_pnl()

    totalRate = totalPnl / account.initial_capital
    for strategy in account.strategies:
        table.add_row(f"{strategy.name}", f"{strategy.pnl:.2f}")


    table.add_row("总收益", f"{totalPnl:.2f}", f"{totalRate:.2%}")
    table.add_row("回测数量", f"{row}" )

    return table

def onNewData(data):

    for strategy in account.strategies:
        strategy.onData(data)

def main():
    with open("strategy1.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
    with open('cleaned_data.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        with Live(makeTable(i), refresh_per_second=1) as live:
            for row in reader:
                if i == 1000:
                    print(".")
                if i in range(0,26560): #8536, 17072
                    onNewData(row)

                    live.update(makeTable(i))
                    print(i)
                i += 1


if __name__ == "__main__":
    main()
