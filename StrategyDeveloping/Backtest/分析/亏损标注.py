import pandas as pd

# 读取 CSV 文件
df = pd.read_csv("strategy2.csv", header=None,
                 names=["time","direction","val1","val2","price"])

# 遍历行，标记 long 行（第四列比下一行 short 的小）
for i in range(len(df)-1):
    if df.loc[i,"direction"] == "long" and df.loc[i+1,"direction"] == "short":
        if df.loc[i,"val2"] < df.loc[i+1,"val2"]:
            # 给 val2 加上标红标记
            df.loc[i,"val2"] = f"RED_{df.loc[i,'val2']}"

# 保存回 CSV（覆盖原文件）
df.to_csv("strategy2.csv", index=False, header=False)
print("已完成标红（RED_ 前缀），结果已写回 your_file.csv ✅")
