import pandas as pd
import numpy as np
import torch
import random
from model import ContrastiveModel
from sklearn.metrics.pairwise import cosine_similarity

# ========= 配置 =========
csv_path = "data/FUN2025.4.15-2025.4.23.csv"
model_path = "trained_contrastive_encoder.pt"
INPUT_DIM = 45
HIDDEN_DIM = 256
NUM_SAMPLES = 10  # 👈 每组取10个

positive_intervals = [
    ("2025-04-15 14:23", "2025-04-15 14:46"),
    ("2025-04-15 21:56", "2025-04-15 22:31"),
    ("2025-04-16 01:00", "2025-04-16 01:36"),
    ("2025-04-16 03:10", "2025-04-16 03:58"),
    ("2025-04-16 17:40", "2025-04-16 18:10"),
    ("2025-04-16 23:50", "2025-04-17 00:20"),
    ("2025-04-18 15:15", "2025-04-18 15:45"),
    ("2025-04-20 13:32", "2025-04-20 14:02"),
    ("2025-04-21 23:01", "2025-04-21 23:31"),
    ("2025-04-22 07:44", "2025-04-22 08:14"),
    ("2025-04-22 13:48", "2025-04-22 14:18"),
    ("2025-04-23 14:04", "2025-04-23 14:34"),
]
negative_intervals = [
    ("2025-04-15 13:30", "2025-04-15 14:10"),
    ("2025-04-15 19:50", "2025-04-15 20:20"),
    ("2025-04-15 23:40", "2025-04-16 00:10"),
    ("2025-04-16 07:30", "2025-04-16 08:00"),
    ("2025-04-16 10:00", "2025-04-16 10:30"),
    ("2025-04-16 11:00", "2025-04-16 11:30"),
    ("2025-04-16 12:30", "2025-04-16 13:00"),
    ("2025-04-16 22:00", "2025-04-16 22:30"),
    ("2025-04-16 22:30", "2025-04-16 23:00"),
    ("2025-04-17 00:20", "2025-04-17 00:50"),
    ("2025-04-17 00:50", "2025-04-17 1:20"),
    ("2025-04-17 1:40", "2025-04-17 2:10"),
    ("2025-04-17 2:08", "2025-04-17 2:38"),
    ("2025-04-19 22:30", "2025-04-19 23:00"),
    ("2025-04-17 00:50", "2025-04-17 1:20"),
    ("2025-04-17 00:50", "2025-04-17 1:20"),
    ("2025-04-22 08:26", "2025-04-22 08:56"),
    ("2025-04-22 09:10", "2025-04-22 09:40"),
    ("2025-04-22 12:40", "2025-04-22 13:10"),
    ("2025-04-22 14:13", "2025-04-22 14:43"),
    ("2025-04-22 15:44", "2025-04-22 16:14"),
    ("2025-04-23 13:43", "2025-04-23 14:13"),
    ("2025-04-23 15:33", "2025-04-23 16:03")
]

# ========= 1. 读取数据 =========
df = pd.read_csv(csv_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])
feature_cols = df.columns.difference(['timestamp', 'label', 'label_enter_uptrend'])

# ========= 2. 加载模型 =========
model = ContrastiveModel(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM)
model.load_state_dict(torch.load(model_path))
model.eval()

# ========= 3. 抽取segment =========
def extract_segment(start, end):
    mask = (df['timestamp'] >= pd.to_datetime(start)) & (df['timestamp'] <= pd.to_datetime(end))
    return df.loc[mask, feature_cols].values  # shape: [T, 45]

positive_segments = [extract_segment(s, e) for s, e in positive_intervals]
negative_segments = [extract_segment(s, e) for s, e in negative_intervals]

# ========= ✅ 相似性测试：正 vs 正 =========
print("🎯 正样本之间相似度（应高）：")
pairs = random.sample(list(enumerate(positive_segments)), NUM_SAMPLES)
for i in range(NUM_SAMPLES):
    idx1, seg1 = pairs[i]
    idx2 = random.choice([j for j in range(len(positive_segments)) if j != idx1])
    seg2 = positive_segments[idx2]

    with torch.no_grad():
        emb1 = model(torch.tensor(seg1, dtype=torch.float32).unsqueeze(0))
        emb2 = model(torch.tensor(seg2, dtype=torch.float32).unsqueeze(0))
        sim = cosine_similarity(emb1.numpy(), emb2.numpy())[0][0]

    print(f"Positive Pair {i+1}: 相似度 = {sim:.4f}")

print("\n---------------------------------------------")

# ========= 🚫 正 vs 负相似度测试（应低） =========
print("🧪 正 vs 负 相似度（应低）：")
for i in range(NUM_SAMPLES):
    pos_idx = random.randint(0, len(positive_segments) - 1)
    neg_idx = random.randint(0, len(negative_segments) - 1)
    seg_pos = positive_segments[pos_idx]
    seg_neg = negative_segments[neg_idx]

    with torch.no_grad():
        emb_pos = model(torch.tensor(seg_pos, dtype=torch.float32).unsqueeze(0))
        emb_neg = model(torch.tensor(seg_neg, dtype=torch.float32).unsqueeze(0))
        sim = cosine_similarity(emb_pos.numpy(), emb_neg.numpy())[0][0]

    print(f"Positive {pos_idx} vs Negative {neg_idx}: 相似度 = {sim:.4f}")
