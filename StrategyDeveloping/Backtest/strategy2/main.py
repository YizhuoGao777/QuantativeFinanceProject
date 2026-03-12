import bisect
import csv
from datetime import datetime

from rich.live import Live
from rich.table import Table
from rich.console import Console
from account import Account
from strategy2 import Strategy1

console = Console()

# 初始化资金账户
account = Account(200)

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
    with open("strategy2.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)


    with (open('../../数据/ETH/CAKE_1h_2024.10-2025.10.csv', newline='', encoding='utf-8') as csvfile1,
          open('../../数据/ETH/CAKE_4h_2024.10-2025.10.csv', newline='', encoding='utf-8') as csvfile2):


        reader2 = list(csv.DictReader(csvfile2))
        reader1 = list(csv.DictReader(csvfile1))
        for r in reader1:
            r["close_time"] = datetime.fromisoformat(r["close_time"])
        for r in reader2:
            r["open_time"] = datetime.fromisoformat(r["open_time"])
            r["close_time"] = datetime.fromisoformat(r["close_time"])
            # 提取 4h open_time 作为查找基准（升序）
            open_times_4h = [r["open_time"] for r in reader2]
        def find_4h_index(target_time):
            """用二分法查找 target_time 属于哪根 4h K线"""
            idx = bisect.bisect_right(open_times_4h, target_time) - 1
            if idx >= 0 and reader2[idx]["open_time"] <= target_time <= reader2[idx]["close_time"]:
                return idx
            return None
        i = 0
        with Live(makeTable(i), refresh_per_second=1) as live:
            for row1 in reader1:
                if i == 1000:
                    print(".")
                if i in range(0,20000): #只处理range里面的row
                    idx = find_4h_index(row1["close_time"])
                    if idx is not None:
                        row4 = reader2[idx]
                        data = [row1, row4]
                        onNewData(data)
                        live.update(makeTable(i))
                        print(i)
                i += 1


if __name__ == "__main__":
    main()
