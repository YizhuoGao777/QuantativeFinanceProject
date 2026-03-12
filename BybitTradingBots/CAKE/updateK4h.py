import time
from datetime import datetime

import pandas as pd
import requests

symbol = "CAKEUSDT"
filename = "CAKE_4h_2024.10-2025.10.csv"
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
        # ====== 转换数值列为浮点型 ======
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        # ====== 1. 计算成交额（价格 × 成交量） ======
        df["amount"] = df["close"] * df["volume"]

        # ====== 2. 计算成交量加权的价格均线（VWEMA） ======
        # 普通 EMA: EMA(close)
        # 成交量加权 EMA: EMA(amount) / EMA(volume)
        df["VWEMA12"] = df["amount"].ewm(span=12, adjust=False).mean() / df["volume"].ewm(span=12,
                                                                                          adjust=False).mean()
        df["VWEMA26"] = df["amount"].ewm(span=26, adjust=False).mean() / df["volume"].ewm(span=26,
                                                                                          adjust=False).mean()

        # ====== 3. 计算 VW-MACD ======
        df["MACD"] = df["VWEMA12"] - df["VWEMA26"]
        df["VW_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["VW_Hist"] = df["MACD"] - df["VW_Signal"]
        # === 4. 写回CSV ===
        df.to_csv(filename, index=False)
        print("写入新k线" + str(k_data))
        # === 6. 等待4小时再执行 ===
        print(f"[{datetime.now()}] 等待下一个小时更新...\n")
        time.sleep(4*3600)


