import pandas as pd

# 你的CSV文件路径
filename = "ETH_1h_2024.10-2025.10.csv"

# 读取CSV
df = pd.read_csv(filename)

# 计算中点位置
half_index = len(df) // 2

# 只保留前一半
df_truncated = df.iloc[half_index:]

# 保存为同名文件（覆盖）
df_truncated.to_csv(filename, index=False)

print(f"已删除后面一半数据，共保留 {half_index} 行。")
