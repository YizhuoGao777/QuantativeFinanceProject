from pybit.unified_trading import HTTP
session = HTTP(
    testnet=False,
    api_key="2MD3WOfgdv7EsmqitD",
    api_secret="1PBZt4q9YliYEWrZ3mxqWeZFlm8qSzMoFaVr",
)
order = session.get_transferable_amount(
    coinName = "USDT"
)
print(order)