from datetime import datetime

from rich.live import Live
from rich.table import Table
from rich.console import Console
from account import Account
from strategy1 import Strategy1
from dataListener import runListener
import asyncio

console = Console()

# 初始化资金账户
account = Account(1000)

Strategy1(account)

# 策略收益快照，用于动态展示

def makeTable():
    table = Table(title="\U0001F4CA 模拟盘收益动态看板" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), expand=True)
    table.add_column("策略名称", justify="left", style="cyan")
    table.add_column("当前持仓收益", justify="right", style="green")
    table.add_column("收益率", justify="right", style="yellow")

    totalPnl = account.total_pnl()

    totalRate = totalPnl / account.initial_capital
    for strategy in account.strategies:
        table.add_row(f"{strategy.name}", f"{strategy.pnl:.2f}")


    table.add_row("总收益", f"{totalPnl:.2f}", f"{totalRate:.2%}")

    return table

def onNewData(data):
    with Live(makeTable(), refresh_per_second=60) as live:
        live.update(makeTable())
    for strategy in account.strategies:
        strategy.onData(data)


async def main():


    async def wrappedCallback(data):
        onNewData(data)

    await runListener(wrappedCallback)

if __name__ == "__main__":
    asyncio.run(main())
