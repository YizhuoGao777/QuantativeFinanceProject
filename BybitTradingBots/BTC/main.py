import csv
from datetime import datetime
import time
import pandas as pd
import requests
from account import Account
from strategy2 import Strategy1


# 初始化资金账户
account = Account(20)

Strategy1(account)


def onNewData(data):

    for strategy in account.strategies:
        strategy.onData(data)

def main():

    symbol = "  BTCUSDT"
    filename = "btc_1h_2024.10-2025.10.csv"
    interval = "1h"
    limit = 1  # 只取最新一根K线
    while True:

        try:
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
            print("已追加新K线")
            # === 3. 计算MACD ===
            df["close"] = df["close"].astype(float)
            df["EMA12"] = df["close"].ewm(span=12, adjust=False).mean()
            df["EMA26"] = df["close"].ewm(span=26, adjust=False).mean()
            df["MACD"] = df["EMA12"] - df["EMA26"]
            df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
            df["Hist"] = df["MACD"] - df["Signal"]
            # === 4. 写回CSV ===
            df.to_csv(filename, index=False)
            print("MACD已更新并保存。")
            # === 5. 取最后3行传给 onNewData ===
            last_rows = df.tail(3).to_dict("records")
            i = len(df) - 3

            ###传数据之前清空策略窗口或者直接传后三行的数据给onNewData

            onNewData(last_rows)
            print(i)
            i += 1

            # === 6. 等待1小时再执行 ===
            print(f"[{datetime.now()}] 等待下一个小时更新...\n")
            time.sleep(3600)

        except Exception as e:
            print("出现错误：", e)
            time.sleep(60)  # 等待一分钟后重试

if __name__ == "__main__":
    main()
