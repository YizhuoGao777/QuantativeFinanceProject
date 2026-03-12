import logging
import time

import requests

ASSET = "BOME"
BUYQUANTITY = "5" ##AUD
RESOLUTION = "1m"
DECREASETHRESHOLD = -0.05
INCREASETHRESHOLD = 0.08
SELLPROPORTION = 0.5
# 配置日志输出到文件
logging.basicConfig(
    filename='BOME.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJrVTRRelF6TlRaQk5rTkNORGsyTnpnME9EYzNOVEZGTWpaRE9USTRNalV6UXpVNE1UUkROUSJ9.eyJodHRwczovL3N3eWZ0eC5jb20uYXUvLWp0aSI6ImViYmI1OTFiLWU4NTItNGYxOS04ZmFjLTkzNGQ1MGY0YzMyZSIsImh0dHBzOi8vc3d5ZnR4LmNvbS5hdS8tbWZhX2VuYWJsZWQiOmZhbHNlLCJodHRwczovL3N3eWZ0eC5jb20uYXUvLXVzZXJVdWlkIjoidXNyX0NRUnJaQXprYnlNV3l5ZGtRaU00cEIiLCJpc3MiOiJodHRwczovL3N3eWZ0eC5hdS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjdlMTRhYjllYzI2NjBjZTc5NDBiMTZiIiwiYXVkIjoiaHR0cHM6Ly9hcGkuc3d5ZnR4LmNvbS5hdS8iLCJpYXQiOjE3NDcxODUwMjgsImV4cCI6MTc0Nzc4OTgyOCwic2NvcGUiOiJhcHAgYXBwLmFjY291bnQgYXBwLmFjY291bnQuYWZmaWxpYXRpb24gYXBwLmFjY291bnQubW9kaWZ5IGFwcC5hY2NvdW50LnRheC1yZXBvcnQgYXBwLmFjY291bnQudmVyaWZpY2F0aW9uIGFwcC5hY2NvdW50LmJhbGFuY2UgYXBwLmFjY291bnQuc3RhdHMgYXBwLmFjY291bnQucmVhZCBhcHAucmVjdXJyaW5nLW9yZGVycyBhcHAucmVjdXJyaW5nLW9yZGVycy5yZWFkIGFwcC5yZWN1cnJpbmctb3JkZXJzLmNyZWF0ZSBhcHAucmVjdXJyaW5nLW9yZGVycy5kZWxldGUgYXBwLmFkZHJlc3MgYXBwLmFkZHJlc3MuYWRkIGFwcC5hZGRyZXNzLnJlbW92ZSBhcHAuYWRkcmVzcy5jaGVjay1kZXBvc2l0IGFwcC5hZGRyZXNzLnJlYWQgYXBwLmZ1bmRzIGFwcC5mdW5kcy53aXRoZHJhdyBhcHAuZnVuZHMud2l0aGRyYXdhbC1saW1pdCBhcHAuZnVuZHMucmVhZCBhcHAub3JkZXJzIGFwcC5vcmRlcnMuY3JlYXRlIGFwcC5vcmRlcnMuZGVsZXRlIGFwcC5vcmRlcnMucmVhZCBhcHAub3JkZXJzLmR1c3QgYXBwLmFwaSBhcHAuYXBpLnJldm9rZSBhcHAuYXBpLnJlYWQgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOlsicmVmcmVzaF90b2tlbiIsInBhc3N3b3JkIl0sImF6cCI6IkVRdzNmYUF4T1RoUllUWnl5MXVsWkRpOERIUkFZZEVPIn0.QtnB6bbdrJnn9HNFPXJbTRmEKIPUFGAoa3ppYqQjbqw53mE7ePEDsu8hZO1gnNs0_Y4p6UF0Ka2U2lRarXFn-8q5Gv3CXcLetklEqCnWtBdZweZiZDkYzHrjYb7FwjjsBBx8TdhuMrKXSNNnf0zwgKJqjhNVpeMwgt2pUJthdFL8RP8B9rEQvnryQHnMjBo7undtLxbPgLof12tdDAn0p5zDyvmqc_sHjMUaRExTyMYh-lg27A8Yj1dkOug5H8MNQz322ODOOCLpxoPQDlKTA9BJyiEtFWqLQiOYNXw5qNLM0tGiqEvKrClMCjVEQd888kFLasggqaU3vUae1AFfXQ"
priceRecord =  0.004462146888067554
positions = [{'rate': 0.004373543467158693, 'amount': 1136.3783251087245, 'sold': 0}]


def refreshToken():
    global token
    values = '''{
      "apiKey": "QykmTqD-q14dpu7XgD6JpFaIq-3kixcAkhfHL1oktFHTS"
    }'''

    headers = {
        'Content-Type': 'application/json'
    }

    token = requests.post('https://api.swyftx.com.au/auth/refresh/', data=values, headers=headers).json()['accessToken']
    logging.info("刷新token。。。")

def getLatestBar():
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MyApp/1.0'
        }

        response = requests.get(f'https://api.swyftx.com.au/charts/v2/getLatestBar/AUD/{ASSET}/ask/?resolution={RESOLUTION}',
                                headers=headers)


        print(response.status_code)
        print(response.json())
        handleData(response.json())

def handleData(json):
    global priceRecord
    try:
        currentPrice = json['close']
    except Exception as e:
        logging.error(e)
    ##判断跌幅并买入
    if currentPrice >= priceRecord:
        priceRecord = currentPrice
    else:
        decrease = (currentPrice - priceRecord) / priceRecord
        print("跌幅：  " + str(decrease))
        if decrease < DECREASETHRESHOLD:
            priceRecord = currentPrice
   ###########################################################         buy()
    ##判断涨幅并卖出
    for position in positions:
        if (currentPrice - position['rate'])/position['rate'] > INCREASETHRESHOLD and position['sold'] == 0:
            sellAmount = position['amount'] * SELLPROPORTION
            if sell(sellAmount) == 200:
                position['amount'] -= sellAmount
                position['sold'] = sellAmount
                logging.info(positions)
    print("price Record:  " +  str(priceRecord))



def buy():
    url = "https://api.swyftx.com.au/orders/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "MyApp/1.0"
    }

    payload = {
        "primary": "AUD",
        "secondary": ASSET,
        "quantity": BUYQUANTITY,
        "assetQuantity": "AUD",
        "orderType": 1,
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 401 and response.json()['error']['error'] == 'TokenExpiredError':
        refreshToken()
        buy()
    if response.status_code == 200:
        json = response.json()
        try:
            position = {"rate": float(json['order']['rate']), "amount": float(json['order']['amount']), "sold": 0}
            positions.append(position)
        except Exception as e:
            logging.error(e)

        print(response.status_code)
        logging.info(response.json())
        logging.info(positions)

def sell(quantity):
    url = "https://api.swyftx.com.au/orders/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "MyApp/1.0"
    }

    payload = {
        "primary": "AUD",
        "secondary": ASSET,
        "quantity": quantity,
        "assetQuantity": ASSET,
        "orderType": 2,
    }

    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code)
    logging.info(response.json())
    if response.status_code == 401 and response.json()['error']['error'] == 'TokenExpiredError':
        refreshToken()
        sell(quantity)

    return response.status_code


while True:
    getLatestBar()
    time.sleep(5)
