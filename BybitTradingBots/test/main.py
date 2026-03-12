import bisect
import csv
import time
from datetime import datetime

import requests
import pandas as pd

from account import Account
from strategy2 import Strategy1


# 初始化资金账户
account = Account(200)

Strategy1(account)

# 策略收益快照，用于动态展示


def onNewData(data):

    for strategy in account.strategies:
        strategy.onData(data)

def main():

    symbol = "ETHUSDT"
    filename = "ETH_1h_2024.10-2025.10(0).csv"
    interval = "1h"
    limit = 1  # 只取最新一根K线
    with open('ETH_1h_2024.10-2025.10.csv', newline='', encoding='utf-8') as f:
        reader1 = list(csv.DictReader(f))
    for r in reader1:

        with open("ETH_1h_2024.10-2025.10(0).csv", "a", newline='', encoding='utf-8') as f2:
            writer = csv.DictWriter(f2,fieldnames=r.keys())
            # 不写表头，直接追加一行
            writer.writerow(r)

            last_rows4h = [] #3条1hk线各自对应的4hk线

            with (open('ETH_1h_2024.10-2025.10(0).csv', newline='', encoding='utf-8') as csvfile1,
                  open('ETH_4h_2024.10-2025.10.csv', newline='', encoding='utf-8') as csvfile2):

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

                last_three_rows = reader1[-3:]

                for row in last_three_rows:
                    idx = find_4h_index(row["close_time"])
                    if idx is not None:
                        row4 = reader2[idx]
                        last_rows4h.append(row4)


            onNewData([last_three_rows,last_rows4h])   ###直接传后三行的数据给onNewData




if __name__ == "__main__":
    main()
