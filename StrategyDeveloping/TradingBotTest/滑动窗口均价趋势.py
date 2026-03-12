import time
from datetime import datetime

import requests
from binance import ThreadedWebsocketManager, Client

ASSET = "CHILLGUY"
QUANTITY = "1" ##AUD
RESOLUTION = "1d"

averageSpan = 4 #平均价格时间长度
consistancy = 20 #趋势持续个数
unchangeTolerence = 3
decreaseTolerence = 1
windowSize = averageSpan + consistancy - 1
bought = False

window = []

def getLatestBar():
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MyApp/1.0'
        }

        response = requests.get(f'https://api.swyftx.com.au/charts/v2/getLatestBar/AUD/{ASSET}/ask/?resolution={RESOLUTION}',
                                headers=headers)

        print("get latest bar:  "+ response.status_code)
        print(response.json())
        handleData(response.json())
        #######解析返回数据用handledata


def handleData(json):
    global bought
    if window.__sizeof__() < windowSize:
        window.append(json)
    else:
        window.pop(0)
        window.append(json)
        if bought == False:
            if checkRising():
                buy()
                bought = True
        else:
            checkDecreasing()


def buy():
    url = "https://api.swyftx.com.au/orders/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJrVTRRelF6TlRaQk5rTkNORGsyTnpnME9EYzNOVEZGTWpaRE9USTRNalV6UXpVNE1UUkROUSJ9.eyJodHRwczovL3N3eWZ0eC5jb20uYXUvLWp0aSI6IjhmOWEwNDJmLWY5NzEtNDQ4NS04NjY0LWU2MWFkYjUyNzNkYSIsImh0dHBzOi8vc3d5ZnR4LmNvbS5hdS8tbWZhX2VuYWJsZWQiOmZhbHNlLCJodHRwczovL3N3eWZ0eC5jb20uYXUvLXVzZXJVdWlkIjoidXNyX0NRUnJaQXprYnlNV3l5ZGtRaU00cEIiLCJpc3MiOiJodHRwczovL3N3eWZ0eC5hdS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjdlMTRhYjllYzI2NjBjZTc5NDBiMTZiIiwiYXVkIjoiaHR0cHM6Ly9hcGkuc3d5ZnR4LmNvbS5hdS8iLCJpYXQiOjE3NDYyNTE1MjMsImV4cCI6MTc0Njg1NjMyMywic2NvcGUiOiJhcHAgYXBwLmFjY291bnQgYXBwLmFjY291bnQuYWZmaWxpYXRpb24gYXBwLmFjY291bnQubW9kaWZ5IGFwcC5hY2NvdW50LnRheC1yZXBvcnQgYXBwLmFjY291bnQudmVyaWZpY2F0aW9uIGFwcC5hY2NvdW50LmJhbGFuY2UgYXBwLmFjY291bnQuc3RhdHMgYXBwLmFjY291bnQucmVhZCBhcHAucmVjdXJyaW5nLW9yZGVycyBhcHAucmVjdXJyaW5nLW9yZGVycy5yZWFkIGFwcC5yZWN1cnJpbmctb3JkZXJzLmNyZWF0ZSBhcHAucmVjdXJyaW5nLW9yZGVycy5kZWxldGUgYXBwLmFkZHJlc3MgYXBwLmFkZHJlc3MuYWRkIGFwcC5hZGRyZXNzLnJlbW92ZSBhcHAuYWRkcmVzcy5jaGVjay1kZXBvc2l0IGFwcC5hZGRyZXNzLnJlYWQgYXBwLmZ1bmRzIGFwcC5mdW5kcy53aXRoZHJhdyBhcHAuZnVuZHMud2l0aGRyYXdhbC1saW1pdCBhcHAuZnVuZHMucmVhZCBhcHAub3JkZXJzIGFwcC5vcmRlcnMuY3JlYXRlIGFwcC5vcmRlcnMuZGVsZXRlIGFwcC5vcmRlcnMucmVhZCBhcHAub3JkZXJzLmR1c3QgYXBwLmFwaSBhcHAuYXBpLnJldm9rZSBhcHAuYXBpLnJlYWQgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOiJwYXNzd29yZCIsImF6cCI6IkVRdzNmYUF4T1RoUllUWnl5MXVsWkRpOERIUkFZZEVPIn0.Ebt9pRI_Au1xqSThDAG9wYhtyAgnUAd00uuaYrB6QWMDsm3sb_fmkEZw2HyIJOks0wkxBgwO1hXiLbf7bm2prNjTHAayUVPQedt59CKlETpRUyEg6CBYMkhTvqD8c2w-l26bYB9MlrghRsL40AZYwpnYgs9lZIRN9BGY7rhDtvIzF2hEwdvWeOYK-EtLLLA6UEVcuxBQ9DqiqcGiUkNmjehNwCDLnvM7TM4tALWMi0Mb8rMOJfsBTn5HfHYk21q0efbpwEfFDahFQEJxewcFJ5kfwgmFyr1WfZZMxc-Vu6DfMuEp31cTgY8tH1AznpuQOw4QWnkSFlgeXlZbumnWbw",
        "User-Agent": "MyApp/1.0"
    }

    payload = {
        "primary": "AUD",
        "secondary": ASSET,
        "quantity": QUANTITY,
        "assetQuantity": "AUD",
        "orderType": 1,
    }

    response = requests.post(url, headers=headers, json=payload)

    print("状态码:", response.status_code)
    print("响应内容:", response.json())
    return True


def checkRising():
    trend = 1
    decreaseCount = 0
    unchangeCount = 0
    previousAverage = 0
    print("\n ============checkRising==============================")
    for j in range(0, consistancy):
        currentAverage = 0
        for i in range(j, j + averageSpan):
            currentAverage += float(window[i]['close']) / averageSpan
        if currentAverage > previousAverage:
            previousAverage = currentAverage
            print(datetime.fromtimestamp(window[i]['time']) + "  " +str(currentAverage) + "  +")
        elif currentAverage == previousAverage:
            previousAverage = currentAverage
            unchangeCount += 1
            print(datetime.fromtimestamp(window[i]['time'])+ "  "+ str(currentAverage) + "  ==")
            if unchangeCount > unchangeTolerence:
                trend = 0
        else:
            previousAverage = currentAverage
            decreaseCount += 1
            print(datetime.fromtimestamp(window[i]['time']) + "  "+ str(currentAverage) + "  -")
            if decreaseCount > decreaseTolerence:
                trend = 0
    if trend == 1:
        print("rising!")
        return True
    else:
        print("not rising!")
        return False

def checkDecreasing():

while not bought:
    getLatestBar()





