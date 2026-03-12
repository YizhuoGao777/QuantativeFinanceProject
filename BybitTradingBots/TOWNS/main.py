import bisect
import csv
import time
from datetime import datetime

import requests
import pandas as pd

from account import Account
from strategy2 import Strategy1


# 初始化资金账户
account = Account(10)

Strategy1(account)

# 策略收益快照，用于动态展示


def onNewData(data):

    for strategy in account.strategies:
        strategy.onData(data)

def main():

    symbol = "TOWNSUSDT"
    filename = "TOWNS_15m_2024.10-2025.10.csv"
    interval = "15m"
    limit = 1  # 只取最新一根K线
    while True:

            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            data = requests.get(url).json()
            if not data or not isinstance(data, list):
                print("API返回数据异常，等待重试...")
                time.sleep(60)
                continue
            ###每小时获取一条最新k线保存并处理
            ##获取一条新k线写入数据并计算macd

            k = data[-1]  # 最新K线
            k_data = {
                "open_time": pd.to_datetime(k[0], unit="ms"),
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": pd.to_datetime(k[6], unit="ms"),
                "quote_asset_volume": float(k[7]),
                "number_of_trades": int(k[8]),
                "taker_buy_base": float(k[9]),
                "taker_buy_quote": float(k[10]),
            }

            print(f"获取到最新K线: {k_data['open_time']}  收盘价={k_data['close']}")

            # === 2. 读取旧数据并添加新K线 ===
            df = pd.read_csv(filename)
            df["open_time"] = pd.to_datetime(df["open_time"])

            df.loc[len(df)] = k_data  # 追加到最后一行

            # === 3. 计算MACD ===
            df["close"] = df["close"].astype(float)
            df["EMA12"] = df["close"].ewm(span=12, adjust=False).mean()
            df["EMA26"] = df["close"].ewm(span=26, adjust=False).mean()
            df["MACD"] = df["EMA12"] - df["EMA26"]
            df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
            df["Hist"] = df["MACD"] - df["Signal"]
            # === 4. 写回CSV ===
            df.to_csv(filename, index=False)
           ### print("写入新k线" + str(k_data))

            last_rows4h = [] #3条1hk线各自对应的4hk线

            with (open('TOWNS_15m_2024.10-2025.10.csv', newline='', encoding='utf-8') as csvfile1,
                  open('TOWNS_1h_2024.10-2025.10.csv', newline='', encoding='utf-8') as csvfile2):

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
                        row4_ = reader2[idx - 1]

                        last_rows4h.append([row4, row4_])  ###当前1hk线对应的4hk线以及上一个4hk线


            onNewData([last_three_rows,last_rows4h])   ###直接传后三行的数据给onNewData


            # === 6. 等待1小时再执行 ===
            print(f"[{datetime.now()}] 等待下一个小时更新...\n")
            time.sleep(900)




if __name__ == "__main__":
    main()
