import pandas as pd
import numpy as np
import torch
from model import ContrastiveModel
from sklearn.metrics.pairwise import cosine_similarity
from datetime import timedelta

# ========= 📁 配置 =========
model_path = "trained_contrastive_encoder.pt"
anchor_csv_path = "data/FUN2025.4.15-2025.4.23.csv"
inference_csv_path = "data/FUN2025.4.15-2025.4.23.csv"
output_path = "similar_windows.csv"

positive_intervals = [
    ("2025-04-15 14:23", "2025-04-15 14:46"),
    ("2025-04-15 21:56", "2025-04-15 22:31"),
    ("2025-04-16 01:00", "2025-04-16 01:36"),
    ("2025-04-16 03:10", "2025-04-16 03:58"),
    ("2025-04-16 17:40", "2025-04-16 18:10"),
    ("2025-04-16 23:50", "2025-04-17 00:20")
]

WINDOW_MINUTES = 30
SIM_THRESHOLD = 0.95

INPUT_DIM = 45
HIDDEN_DIM = 256

# ========= 🔁 加载数据 & 模型 =========
anchor_df = pd.read_csv(anchor_csv_path)
anchor_df['timestamp'] = pd.to_datetime(anchor_df['timestamp'])
feature_cols = anchor_df.columns.difference(['timestamp', 'label', 'label_enter_uptrend'])

model = ContrastiveModel(input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM)
model.load_state_dict(torch.load(model_path))
model.eval()

# ========= 📌 提取 anchor embedding =========
def extract_segment(df, start, end):
    mask = (df['timestamp'] >= pd.to_datetime(start)) & (df['timestamp'] <= pd.to_datetime(end))
    return df.loc[mask, feature_cols].values

anchor_embeddings = []
for start, end in positive_intervals:
    seg = extract_segment(anchor_df, start, end)
    with torch.no_grad():
        emb = model(torch.tensor(seg, dtype=torch.float32).unsqueeze(0))
        anchor_embeddings.append(emb.squeeze(0).numpy())

# ========= 📊 加载 inference 数据 =========
inference_df = pd.read_csv(inference_csv_path)
inference_df['timestamp'] = pd.to_datetime(inference_df['timestamp'])
inference_df = inference_df.sort_values('timestamp').reset_index(drop=True)

timestamps = inference_df['timestamp'].tolist()
matched_times = []

# ========= ⏱ 滑动窗口遍历 =========

# 把所有 timestamps 提前提出来
i = 0
while i < len(timestamps):
    start_time = timestamps[i]
    end_time = start_time + timedelta(minutes=WINDOW_MINUTES)

    # 找到窗口末尾在 timestamps 中对应的位置 j
    try:
        j = timestamps.index(end_time)
    except ValueError:
        # 如果 end_time 不存在于数据中，就找最接近的那个
        valid_times = [t for t in timestamps if t > start_time and t <= end_time]
        if not valid_times:
            i += 1  # ✅ 修改为跳过本轮，继续滑动
            continue
        end_time = valid_times[-1]
        j = timestamps.index(end_time)

    # 提取当前窗口数据
    window_mask = (inference_df['timestamp'] >= start_time) & (inference_df['timestamp'] <= end_time)
    window_segment = inference_df.loc[window_mask, feature_cols].values

    if len(window_segment) < WINDOW_MINUTES:
        i += 1
        continue

    with torch.no_grad():
        window_emb = model(torch.tensor(window_segment, dtype=torch.float32).unsqueeze(0)).numpy()

    # 是否命中任意 anchor？
    hit = False
    for anchor_emb in anchor_embeddings:
        sim = cosine_similarity(window_emb, anchor_emb.reshape(1, -1))[0][0]
        if sim >= SIM_THRESHOLD:
            matched_times.append(end_time)
            hit = True
            break

    # 命中 → 跳过这段窗口，继续后滑
    if hit:
        i = j + 1
    else:
        i += 1

# ========= 💾 保存结果 =========
result_df = pd.DataFrame({'matched_end_time': matched_times})
result_df.to_csv(output_path, index=False)
print(f"✅ 相似窗口已保存至 {output_path}，共匹配到 {len(matched_times)} 个时间段")
