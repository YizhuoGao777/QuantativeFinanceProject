import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def runListener(callback):
    selectors = {
        "资金费率": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(5) > div > div > a",
        "价格": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(4) > a > div",
        "OI（1h%）": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(6) > div",
        "Long Liquidation(1h)": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(7) > div",
        "Short Liquidation(1h)": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(8) > div",
        "Top Trader L/S (Positions)": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(9) > div",
        "Top Trader L/S (Accounts)": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(10) > div",
        "L/S (Positions)": "#__next > div:nth-child(2) > div.cg-content.MuiBox-root.cg-style-vsqgwu > div.plr20 > div.ant-table-wrapper > div > div > div > div > div.ant-table-body > table > tbody > tr:nth-child(3) > td:nth-child(11) > div"

    }

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]

        while True:
            data = {}
            for label, selector in selectors.items():
                try:
                    el = await page.query_selector(selector)
                    if el:
                        data[label] = await el.inner_text()
                except:
                    data[label] = "N/A"
            data["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await callback(data)

            await asyncio.sleep(60)
