import requests
import pandas as pd

# 获取 SAGA/USDT 的 1日K线数据
url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": "SAGAUSDT",
    "interval": "1d",
    "limit": 100  # 最多可获取1000条数据
}

response = requests.get(url, params=params)
data = response.json()

# 设置列名
columns = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
]

# 转换为 DataFrame 并格式化时间
df = pd.DataFrame(data, columns=columns)
df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')

# 保存为 CSV 文件
df.to_csv("saga_usdt_1d.csv", index=False)

print("已保存为 saga_usdt_1d.csv")
