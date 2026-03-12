import pandas as pd
import numpy as np

# ==== 配置路径 ====
csv_path = "FUN_训练打标签版.csv"  # 你的 CSV 数据路径
output_path = "训练数据.npz"  # 输出的 .npz 文件名

# ==== 设置上涨前段区间（用于 anchor 和 positive） ====
positive_intervals = [
    ("2025-04-15 14:23", "2025-04-15 14:46"),
    ("2025-04-15 21:56", "2025-04-15 22:31"),
    ("2025-04-16 01:00", "2025-04-16 01:36"),
    ("2025-04-16 03:10", "2025-04-16 03:58"),
]

# ==== 设置负样本区间（普通段） ====
negative_intervals = [
    ("2025-04-15 15:40", "2025-04-15 16:20"),
    ("2025-04-15 19:20", "2025-04-15 20:00"),
    ("2025-04-16 00:00", "2025-04-16 00:40"),
    ("2025-04-16 07:10", "2025-04-16 07:50"),
]

# ==== 读取 CSV ====
df = pd.read_csv(csv_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# 自动排除时间和标签列，只保留特征列
feature_cols = df.columns.difference(['timestamp', 'label', 'label_enter_uptrend'])

# ==== 提取段数据 ====
positives, negatives = [], []

def extract_segment(start, end):
    mask = (df['timestamp'] >= pd.to_datetime(start)) & (df['timestamp'] <= pd.to_datetime(end))
    return df.loc[mask, feature_cols].values

for start, end in positive_intervals:
    positives.append(extract_segment(start, end))

for start, end in negative_intervals:
    negatives.append(extract_segment(start, end))
print(positives[0])
print(negatives[0])
# ==== 构造三元组：anchor-positive-negative ====
anchor_list, positive_list, negative_list = [], [], []

for i in range(len(positives)):
    for j in range(len(positives)):
        if i != j:
            anchor = positives[i]
            positive = positives[j]
            negative = negatives[np.random.randint(0, len(negatives))]

            anchor_list.append(anchor)
            positive_list.append(positive)
            negative_list.append(negative)

# ==== 保存为 .npz ====
np.savez_compressed(output_path,
                    anchor=np.array(anchor_list, dtype=object),
                    positive=np.array(positive_list, dtype=object),
                    negative=np.array(negative_list, dtype=object))

print(f"✅ 成功保存对比学习训练数据为：{output_path}")
