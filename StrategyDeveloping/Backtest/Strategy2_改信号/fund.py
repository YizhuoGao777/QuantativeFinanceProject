import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def fund():
    # === 1. 读取 CSV ===
    df = pd.read_csv("strategy2.csv", header=None)
    df.columns = ["time", "position", "ratio", "funds", "price"]

    # === 2. 转换数据格式 ===
    df["time"] = pd.to_datetime(df["time"])
    df["funds"] = df["funds"].astype(float)
    df["price"] = df["price"].astype(float)

    # === 3. 计算胜率 ===
    win_count = 0
    trade_count = 0
    profits = []
    losses = []

    for i in range(0, len(df) - 1, 2):
        entry_price = df.loc[i, "price"]
        exit_price = df.loc[i + 1, "price"]
        direction = df.loc[i, "position"].lower()
        diff = exit_price - entry_price

        if direction == "long":
            if diff > 0:
                win_count += 1
            pl = diff
        else:  # short
            if diff < 0:
                win_count += 1
            pl = -diff

        if pl > 0:
            profits.append(pl)
        elif pl < 0:
            losses.append(pl)

        trade_count += 1

    win_rate = win_count / trade_count if trade_count > 0 else np.nan
    avg_win = np.mean(profits) if profits else 0
    avg_loss = np.mean(losses) if losses else 0
    profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else np.nan

    # === 4. 只取奇数行绘图 ===
    df_plot = df.iloc[::2].reset_index(drop=True)

    # === 5. 最大回撤（基于奇数行资金） ===
    df_plot["peak"] = df_plot["funds"].cummax()
    df_plot["drawdown"] = (df_plot["funds"] - df_plot["peak"]) / df_plot["peak"]
    max_drawdown = df_plot["drawdown"].min()
    end_idx = df_plot["drawdown"].idxmin()
    start_idx = df_plot.loc[:end_idx, "funds"].idxmax()

    # === 6. 夏普比（基于资金曲线收益率） ===
    df_plot["return"] = df_plot["funds"].pct_change()
    sharpe_ratio = (
        (df_plot["return"].mean() / df_plot["return"].std()) * np.sqrt(252)
        if df_plot["return"].std() != 0
        else np.nan
    )

    # === 7. 绘图 ===
    plt.figure(figsize=(24, 12))
    plt.plot(df_plot["time"], df_plot["funds"], color="black", linewidth=1.8, label="fund（奇数行）")
    plt.fill_between(df_plot["time"], df_plot["funds"], df_plot["peak"], color="red", alpha=0.1, label="drawdown range")

    plt.scatter(df_plot["time"].iloc[start_idx], df_plot["funds"].iloc[start_idx], color="green", label="Peak")
    plt.scatter(df_plot["time"].iloc[end_idx], df_plot["funds"].iloc[end_idx], color="red", label="low")
    plt.plot(
        [df_plot["time"].iloc[start_idx], df_plot["time"].iloc[end_idx]],
        [df_plot["funds"].iloc[start_idx], df_plot["funds"].iloc[end_idx]],
        color="orange", linestyle="--", linewidth=2, label="最大回撤区间"
    )

    plt.title(f"funding change（max_drawdown：{max_drawdown:.2%}）", fontsize=24)
    plt.xlabel("time", fontsize=24)
    plt.ylabel("fund", fontsize=24)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()

    # === 8. 输出结果 ===
    print("====== 策略绩效指标 ======")
    print(f"交易次数（Trades）: {trade_count}")
    print(f"胜率（Win Rate）: {win_rate:.2%}")
    print(f"盈亏比（Profit/Loss Ratio）: {profit_loss_ratio:.2f}")
    print(f"夏普比（Sharpe Ratio）: {sharpe_ratio:.2f}")
    print("----------------------------")
    print(f"最大回撤（Max Drawdown）: {max_drawdown:.2%}")
    print(f"峰值时间: {df_plot['time'].iloc[start_idx]}")
    print(f"谷值时间: {df_plot['time'].iloc[end_idx]}")
    print(f"峰值资金: {df_plot['funds'].iloc[start_idx]:.2f}")
    print(f"谷值资金: {df_plot['funds'].iloc[end_idx]:.2f}")

