import csv
import pandas as pd
import requests


ASSET = "CTK"
INTERVAL = "5m"


url = "https://api.binance.com/api/v3/klines"
params = {
    "symbol": ASSET+"USDT",
    "interval": INTERVAL,
    "limit": 500  # 最多可获取1000条数据
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())
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

rows = []
with open('saga_usdt_1d.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        rows.append(row)
print(rows[:5])  # 打印前5行看一下结构

averageSpan = 5 #平均价格时间长度
consistancy = 500 #趋势持续个数
unchangeTolerence = 3
decreaseTolerence = 3

trend = 1
decreaseCount = 0
unchangeCount = 0
previousAverage = 0
for j in range(0, consistancy):
    currentAverage = 0
    for i in range(j, j + averageSpan):
        currentAverage += float(rows[i][4]) / averageSpan
    if currentAverage > previousAverage:
        previousAverage = currentAverage
        print(rows[i][0] + "  " +str(currentAverage) + "  +")
    elif currentAverage == previousAverage:
        previousAverage = currentAverage
        unchangeCount += 1
        print(rows[i][0]+ "  "+ str(currentAverage) + "  ==")
        if unchangeCount > unchangeTolerence:
            trend = 0
    else:
        previousAverage = currentAverage
        decreaseCount += 1
        print(rows[i][0] + "  "+ str(currentAverage) + "  -")
        if decreaseCount > decreaseTolerence:
            trend = 0
if trend == 1:
    print("rising!")
else:
    print("not rising!")


