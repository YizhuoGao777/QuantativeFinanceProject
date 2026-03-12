import pandas as pd
import numpy as np
from ta.trend import ADXIndicator

# === 参数设置 ===
input_file = "ETH_15m_2024.10-2025.10.csv"  # 你的原始数据文件
output_file = "ETH_15m_2024.10-2025.10.csv"
window = 20  # 计算窗口期，可调整
w1, w2, w3 = 0.2, 0.6, 0.2  # 权重，可调

# === 读取数据 ===
df = pd.read_csv(input_file)

# 确保列名
# 若你的CSV有 open/high/low/close/volume 这类列就可以直接使用
if not set(["close", "high", "low"]).issubset(df.columns):
    raise ValueError("CSV中必须包含 'close', 'high', 'low' 列用于计算ADX")

# 若没有volume，可以用虚拟volume替代（但ΔVol/ΔVolatility项会失真）
if "volume" not in df.columns:
    df["volume"] = 1.0

# === 计算 ρ(1)：价格一阶自相关 ===
df["return"] = df["close"].pct_change()
df["rho1"] = df["return"].rolling(window).apply(lambda x: x.autocorr(lag=1))

# === 计算 ADX ===
adx = ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=window)
df["ADX"] = adx.adx()

# === 计算波动率变化与成交量变化 ===
df["volatility"] = df["return"].rolling(window).std()
df["delta_volatility"] = df["volatility"].diff()
df["delta_volume"] = df["volume"].diff()

# 避免除零
df["vol_vol_ratio"] = np.where(df["delta_volume"] != 0,
                               df["delta_volatility"] / df["delta_volume"],
                               np.nan)

# === 计算 TrendScore ===
df["TrendScore"] = (w1 * df["rho1"] +
                    w2 * df["ADX"].fillna(0) +
                    w3 * df["vol_vol_ratio"].fillna(0))

# === 输出结果 ===
df.to_csv(output_file, index=False)
print(f"✅ TrendScore 已写入 {output_file}")
