import random

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from model import ContrastiveModel
from loss import contrastive_loss

# ========= 📁 1. 读取CSV + 提取样本 =========
csv_path = "data/FUN2025.4.15-2025.4.23.csv"
df = pd.read_csv(csv_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])
feature_cols = df.columns.difference(['timestamp', 'label', 'label_enter_uptrend'])

# ==== 设置你的正样本段（上涨前段）====
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

# ==== 设置负样本段（普通震荡段）====
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

def extract_segment(start, end):
    mask = (df['timestamp'] >= pd.to_datetime(start)) & (df['timestamp'] <= pd.to_datetime(end))
    return df.loc[mask, feature_cols].values

positive_segments = [extract_segment(s, e) for s, e in positive_intervals]
negative_segments = [extract_segment(s, e) for s, e in negative_intervals]

# ========= 🧱 2. 定义 Dataset =========
class ContrastiveTripletDataset(Dataset):
    def __init__(self, positives, negatives, negatives_per_pair=5):
        self.anchor_list = []
        self.positive_list = []
        self.negative_list = []

        for i in range(len(positives)):
            for j in range(len(positives)):
                if i != j:
                    anchor = torch.tensor(positives[i], dtype=torch.float32)
                    positive = torch.tensor(positives[j], dtype=torch.float32)

                    # 为每一对 anchor–positive 配多个不同的 negative
                    selected_negatives = random.choices(negatives, k=negatives_per_pair)
                    for neg in selected_negatives:
                        negative = torch.tensor(neg, dtype=torch.float32)

                        self.anchor_list.append(anchor)
                        self.positive_list.append(positive)
                        self.negative_list.append(negative)

    def __len__(self):
        return len(self.anchor_list)

    def __getitem__(self, idx):
        return self.anchor_list[idx], self.positive_list[idx], self.negative_list[idx]


# ========= 📦 3. Collate函数：自动padding =========
from torch.nn.utils.rnn import pad_sequence
def collate_fn(batch):
    anchors, positives, negatives = zip(*batch)

    def pad_batch(batch):
        return pad_sequence(batch, batch_first=True)

    return pad_batch(anchors), pad_batch(positives), pad_batch(negatives)

# ========= ⚙️ 4. 初始化模型 =========
model = ContrastiveModel(input_dim=45, hidden_dim=256)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

# ========= 🏋️ 5. 加载数据并训练 =========
dataset = ContrastiveTripletDataset(positive_segments, negative_segments)
loader = DataLoader(dataset, batch_size=12, shuffle=True, collate_fn=collate_fn)

for epoch in range(60):
    model.train()
    total_loss = 0
    for anchor, positive, negative in loader:
        z_anchor = model(anchor)
        z_positive = model(positive)
        z_negative = model(negative)

        loss = contrastive_loss(z_anchor, z_positive, z_negative)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss:.4f}")
    if total_loss < 0.3:
        torch.save(model.state_dict(), "trained_contrastive_encoder.pt")
        print("✅ 模型已保存为 trained_contrastive_encoder.pt")
        break

