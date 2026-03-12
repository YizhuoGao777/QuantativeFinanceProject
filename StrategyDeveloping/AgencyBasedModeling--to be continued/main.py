# main.py
import random
import numpy as np

from individual import Individual
from product import FinancialProduct


def create_population(num_individuals: int = 1000,
                      behavior_mean: float = 400,
                      behavior_std: float = 300,
                      noise_percentile: float = 10.0):
    """
    使用正态分布为每个个体生成“行为阈值”，并把阈值最低的一部分人标记为噪声交易者。

    - behavior_mean / std: 控制阈值分布（你之前说想用 1~1000，就用 500.5 / 166.5）
    - noise_percentile: “阈值极低”的比例，比如 10 表示最低 10% 的人是 noise trader
    """
    behavior_thresholds = np.random.normal(
        loc=behavior_mean,
        scale=behavior_std,
        size=num_individuals
    )

    # 防止出现 0 或负值，简单 clip 一下
    behavior_thresholds = np.clip(behavior_thresholds, 1.0, None)

    # 找出“阈值极低”的那一批人 -> 噪声交易者
    cutoff = np.percentile(behavior_thresholds, noise_percentile)

    individuals = []
    for th in behavior_thresholds:
        is_noise = th <= cutoff
        ind = Individual(behavior_threshold=th, is_noise_trader=is_noise)
        individuals.append(ind)

    return individuals


def simulate(num_ticks: int = 100,
             num_individuals: int = 1000,
             seed: int = 42):
    """
    运行整个系统的模拟。

    价格规则（每个 tick）：
        多方向 =  新开多数量 + 平空数量  （买）
        空方向 =  新开空数量 + 平多数量  （卖）

        order_flow = 多方向 - 空方向
        price += order_flow
    """
    np.random.seed(seed)
    random.seed(seed)

    product = FinancialProduct(initial_price=1000.0)
    individuals = create_population(num_individuals=num_individuals)

    price_history = [product.price]

    long_open_history = []
    short_open_history = []
    long_close_history = []
    short_close_history = []

    prev_price = product.price  # 初始假定上一 tick 价格也是 1000

    for tick in range(num_ticks):
        long_open = 0   # 新开多
        short_open = 0  # 新开空
        long_close = 0  # 平多
        short_close = 0 # 平空

        price_change = product.price - prev_price

        # ✅ 所有 tick（包括第 0 个），统一行为逻辑：
        for ind in individuals:
            open_action, close_action = ind.decide(price_change)

            # 开仓行为
            if open_action == +1:
                long_open += 1
            elif open_action == -1:
                short_open += 1

            # 平仓行为
            # close_action: +1 = 平空（买，多方向），-1 = 平多（卖，空方向）
            if close_action == +1:
                short_close += 1
            elif close_action == -1:
                long_close += 1

        # ====== tick 结束：根据所有交易更新价格 ======
        net_buy = long_open + short_close     # 多方向交易
        net_sell = short_open + long_close    # 空方向交易
        order_flow = net_buy - net_sell

        prev_price = product.price
        product.price += order_flow

        # 记录数据
        long_open_history.append(long_open)
        short_open_history.append(short_open)
        long_close_history.append(long_close)
        short_close_history.append(short_close)
        price_history.append(product.price)

        print(
            f"Tick {tick:3d} | "
            f"Price: {product.price:8.2f} | "
            f"Open L/S: {long_open:4d}/{short_open:4d} | "
            f"Close L/S: {long_close:4d}/{short_close:4d} | "
            f"OrderFlow: {order_flow:5d}"
        )

    return {
        "price_history": price_history,
        "long_open_history": long_open_history,
        "short_open_history": short_open_history,
        "long_close_history": long_close_history,
        "short_close_history": short_close_history,
        "individuals": individuals,
    }


if __name__ == "__main__":
    result = simulate(num_ticks=300, num_individuals=1000, seed=None)
    print("\nFinal price:", result["price_history"][-1])
    import matplotlib.pyplot as plt

    price = result["price_history"]
    long_open = np.array(result["long_open_history"])
    short_open = np.array(result["short_open_history"])
    long_close = np.array(result["long_close_history"])
    short_close = np.array(result["short_close_history"])

    # 计算每个 tick 总持仓方向（多减空）
    net_positions = long_open - short_open - long_close + short_close

    ticks = range(len(price))

    plt.figure(figsize=(14, 6))
    plt.plot(ticks, price, label="Price")
    plt.plot(ticks[:-1], net_positions, label="Net Position (long-short)", alpha=0.7)

    plt.title("Price & Net Positions Over Time")
    plt.xlabel("Tick")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
