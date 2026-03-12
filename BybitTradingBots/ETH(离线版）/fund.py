import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === 1. 读取 CSV ===
df = pd.read_csv("strategy2.csv", header=None)
df.columns = ["time", "position", "ratio", "funds", "price"]

# === 2. 转换时间格式 ===
df["time"] = pd.to_datetime(df["time"])
df["funds"] = df["funds"].astype(float)

# === 3. 计算最大回撤 ===
# 累计资金最高值
df["peak"] = df["funds"].cummax()

# 回撤比率（从峰值回落的比例）
df["drawdown"] = (df["funds"] - df["peak"]) / df["peak"]

# 最大回撤及对应时间点
max_drawdown = df["drawdown"].min()
end_idx = df["drawdown"].idxmin()
start_idx = df.loc[:end_idx, "funds"].idxmax()

# === 4. 绘图 ===
plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["funds"], color="steelblue", linewidth=1.8, label="资金变化")
plt.fill_between(df["time"], df["funds"], df["peak"], color="red", alpha=0.1, label="回撤区域")

# 标出最大回撤区间
plt.scatter(df["time"].iloc[start_idx], df["funds"].iloc[start_idx], color="green", label="峰值点")
plt.scatter(df["time"].iloc[end_idx], df["funds"].iloc[end_idx], color="red", label="谷值点")
plt.plot(
    [df["time"].iloc[start_idx], df["time"].iloc[end_idx]],
    [df["funds"].iloc[start_idx], df["funds"].iloc[end_idx]],
    color="orange", linestyle="--", linewidth=2, label="最大回撤区间"
)

# === 5. 美化图表 ===
plt.title(f"资金变化趋势（最大回撤：{max_drawdown:.2%}）", fontsize=14)
plt.xlabel("时间", fontsize=12)
plt.ylabel("资金", fontsize=12)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.xticks(rotation=30)
plt.tight_layout()

# === 6. 显示图表 ===
plt.show()

# === 7. 打印结果 ===
print(f"最大回撤（Max Drawdown）: {max_drawdown:.2%}")
print(f"峰值时间: {df['time'].iloc[start_idx]}")
print(f"谷值时间: {df['time'].iloc[end_idx]}")
print(f"峰值资金: {df['funds'].iloc[start_idx]:.2f}")
print(f"谷值资金: {df['funds'].iloc[end_idx]:.2f}")
