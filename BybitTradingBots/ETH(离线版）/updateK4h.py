import time
from datetime import datetime

import pandas as pd
import requests

symbol = "ETHUSDT"
filename = "ETH_4h_2024.10-2025.10.csv"
interval = "4h"
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
        print("写入新k线" + str(k_data))
        # === 6. 等待4小时再执行 ===
        print(f"[{datetime.now()}] 等待下一个小时更新...\n")
        time.sleep(4*3600)


