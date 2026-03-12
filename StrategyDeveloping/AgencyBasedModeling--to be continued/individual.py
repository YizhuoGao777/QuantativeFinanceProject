# individual.py
import random


class Individual:
    """
    个体（投资者）

    - behavior_threshold: 行为阈值（一个参数同时控制开仓 & 平仓频率）
        * 空仓时：
            |价格变动| >= 行为阈值 -> 考虑入场
              - 价格上涨 -> 开多仓（买，多方向）
              - 价格下跌 -> 开空仓（卖，空方向）
        * 有持仓时：
            |价格变动| <= 行为阈值 -> 考虑平仓
              - 平多仓 -> 卖（空方向）
              - 平空仓 -> 买（多方向）
        * 阈值越低，越容易触发行为，交易越频繁

    - is_noise_trader: 是否为“极低阈值的噪声交易者”
        * 如果他当前空仓，且本 tick 没有触发正常入场条件，
          那么他会随机开多或开空（每个 tick 都可能这样做，不只第一个 tick）。

    - position: 当前持仓状态，1=多头，-1=空头，0=空仓
    """
    def __init__(self, behavior_threshold: float, is_noise_trader: bool = False):
        self.behavior_threshold = float(behavior_threshold)
        self.is_noise_trader = bool(is_noise_trader)
        self.position = 0  # 1 = long, -1 = short, 0 = flat

    def decide(self, price_change: float) -> tuple[int, int]:
        """
        根据当前价格变动决定行为。

        参数：
            price_change: 当前价格 - 上一 tick 价格

        返回 (open_action, close_action)：
            open_action:
                +1 -> 本 tick 新开多仓（买，多方向，价格上涨）
                -1 -> 本 tick 新开空仓（卖，空方向，价格下降）
                 0 -> 不开新仓

            close_action:
                +1 -> 平空仓（买，多方向，价格上涨）
                -1 -> 平多仓（卖，空方向，价格下降）
                 0 -> 不平仓

        约束：
        - 每个个体每个 tick 最多只做一次行为：
            要么平仓，要么开仓，要么啥也不做。
        - 逻辑优先级：
            1. 有持仓 -> 先看要不要平仓（满足条件就只平仓，不再开新仓）
            2. 空仓 ->
                a) 如果满足“正常开仓条件”：按价格方向开仓
                b) 否则如果是噪声交易者：随机开多/开空
        """
        open_action = 0
        close_action = 0
        threshold = self.behavior_threshold

        # 1️⃣ 有持仓时：只考虑平仓
        # 1️⃣ 有持仓：根据方向判断是否平仓
        if self.position != 0:
            # 多仓：价格上涨超过阈值 → 平多
            if self.position == 1 and price_change >= threshold:
                self.position = 0
                close_action = -1  # 平多 = 卖 = 空方向

            # 空仓：价格下跌超过阈值 → 平空
            elif self.position == -1 and -price_change >= threshold:
                self.position = 0
                close_action = +1  # 平空 = 买 = 多方向

            # 无论是否平仓，这个 tick 都结束
            return open_action, close_action

        # 2️⃣ 当前空仓：先尝试“正常开仓逻辑”
        if abs(price_change) >= threshold and price_change != 0:
            if price_change > 0:
                # 价格上涨 -> 顺势开多（买，多方向）
                self.position = 1
                open_action = +1
            elif price_change < 0:
                # 价格下跌 -> 顺势开空（卖，空方向）
                self.position = -1
                open_action = -1

            return open_action, close_action

        # 3️⃣ 正常开仓条件没有触发，如果是噪声交易者 -> 随机开仓
        if self.is_noise_trader:
            # 每个 tick 只要他是空仓，就会随机开多/开空，
            # 你也可以改成加一个概率，比如 if random.random() < 0.3 再随机。
            self.position = random.choice([1, -1])
            open_action = self.position  # 多=+1（买），空=-1（卖）
            return open_action, close_action

        # 4️⃣ 不是噪声交易者 & 没有信号 -> 本 tick 什么也不做
        return open_action, close_action
