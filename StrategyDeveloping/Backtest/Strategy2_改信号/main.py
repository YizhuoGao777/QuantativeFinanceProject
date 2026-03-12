import bisect
import csv
from datetime import datetime
import fund
import pandas as pd

from rich.live import Live
from rich.table import Table
from rich.console import Console
from account import Account
from strategy2 import Strategy1

console = Console()

# 初始化资金账户
account = Account(100)

symbol = "ETH"
period = "2024.10-2025.10"
logFile = symbol+ period + ".csv"
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

def make_partial_4h_with_macd(row1, reader1, reader2, idx):
    """生成截止到当前30min收盘的不完整4h线，并计算包含MACD的动态值"""
    row4_current = reader2[idx]
    start_4h = row4_current["open_time"]
    end_4h = row4_current["close_time"]

    # ===== 1️⃣ 聚合当前4h内的30m数据 =====



    close_ = row1["close"]


    # ===== 2️⃣ 生成不完整K线对象 =====
    partial_4h = {
        "open_time": start_4h,
        "close_time": row1["close_time"],
        "open": 0,
        "high": 0,
        "low": 0,
        "close": close_,
        "volume": 0,
        "incomplete": True
    }

    # ===== 3️⃣ 计算 MACD（含该partial） =====
    df = pd.DataFrame(reader2)
    df = df.astype({"open": float, "high": float, "low": float, "close": float})
    df["open_time"] = pd.to_datetime(df["open_time"])
    df["close_time"] = pd.to_datetime(df["close_time"])

    # 加上当前未收盘的这根K线
    df = pd.concat([df, pd.DataFrame([partial_4h])], ignore_index=True)

    # MACD 计算
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    # 获取当前这根的MACD值
    partial_4h["MACD"] = float(macd.iloc[-1])
    partial_4h["Signal"] = float(signal.iloc[-1])
    partial_4h["Hist"] = float(hist.iloc[-1])

    return partial_4h

def onNewData(data):

    for strategy in account.strategies:
        strategy.onData(data)

def main():
    with open("strategy2.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)


    with (open(f'../../数据/ETH/{symbol}_30m_{period}.csv', newline='', encoding='utf-8') as csvfile1,
          open(f'../../数据/ETH/{symbol}_4h_{period}.csv', newline='', encoding='utf-8') as csvfile2):


        reader2 = list(csv.DictReader(csvfile2))
        reader1 = list(csv.DictReader(csvfile1))
        for r in reader1:
            r["open_time"] = datetime.fromisoformat(r["close_time"])
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
                if i in range(0,18000): #只处理range里面的row



                    idx = find_4h_index(row1["close_time"])
                    if idx is not None:
                        row4 = make_partial_4h_with_macd(row1, reader1, reader2, idx)
                        row4_ = reader2[idx - 1]  ####上一条4hk线   make_partial_4h_with_macd(row1, reader1, reader2, idx)
                        row4__ = reader2[idx - 3]

                        data = [row1, row4, row4_, row4__]
                        onNewData(data)
                        live.update(makeTable(i))
                        print(i)
                i += 1
            fund.fund()




if __name__ == "__main__":
    main()
