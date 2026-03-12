import time

import requests
ASSET = "ETH"
QUANTITY = "500" ##AUD
RESOLUTION = "1m"
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlJrVTRRelF6TlRaQk5rTkNORGsyTnpnME9EYzNOVEZGTWpaRE9USTRNalV6UXpVNE1UUkROUSJ9.eyJodHRwczovL3N3eWZ0eC5jb20uYXUvLWp0aSI6ImViYmI1OTFiLWU4NTItNGYxOS04ZmFjLTkzNGQ1MGY0YzMyZSIsImh0dHBzOi8vc3d5ZnR4LmNvbS5hdS8tbWZhX2VuYWJsZWQiOmZhbHNlLCJodHRwczovL3N3eWZ0eC5jb20uYXUvLXVzZXJVdWlkIjoidXNyX0NRUnJaQXprYnlNV3l5ZGtRaU00cEIiLCJpc3MiOiJodHRwczovL3N3eWZ0eC5hdS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjdlMTRhYjllYzI2NjBjZTc5NDBiMTZiIiwiYXVkIjoiaHR0cHM6Ly9hcGkuc3d5ZnR4LmNvbS5hdS8iLCJpYXQiOjE3NDcxODUwMjgsImV4cCI6MTc0Nzc4OTgyOCwic2NvcGUiOiJhcHAgYXBwLmFjY291bnQgYXBwLmFjY291bnQuYWZmaWxpYXRpb24gYXBwLmFjY291bnQubW9kaWZ5IGFwcC5hY2NvdW50LnRheC1yZXBvcnQgYXBwLmFjY291bnQudmVyaWZpY2F0aW9uIGFwcC5hY2NvdW50LmJhbGFuY2UgYXBwLmFjY291bnQuc3RhdHMgYXBwLmFjY291bnQucmVhZCBhcHAucmVjdXJyaW5nLW9yZGVycyBhcHAucmVjdXJyaW5nLW9yZGVycy5yZWFkIGFwcC5yZWN1cnJpbmctb3JkZXJzLmNyZWF0ZSBhcHAucmVjdXJyaW5nLW9yZGVycy5kZWxldGUgYXBwLmFkZHJlc3MgYXBwLmFkZHJlc3MuYWRkIGFwcC5hZGRyZXNzLnJlbW92ZSBhcHAuYWRkcmVzcy5jaGVjay1kZXBvc2l0IGFwcC5hZGRyZXNzLnJlYWQgYXBwLmZ1bmRzIGFwcC5mdW5kcy53aXRoZHJhdyBhcHAuZnVuZHMud2l0aGRyYXdhbC1saW1pdCBhcHAuZnVuZHMucmVhZCBhcHAub3JkZXJzIGFwcC5vcmRlcnMuY3JlYXRlIGFwcC5vcmRlcnMuZGVsZXRlIGFwcC5vcmRlcnMucmVhZCBhcHAub3JkZXJzLmR1c3QgYXBwLmFwaSBhcHAuYXBpLnJldm9rZSBhcHAuYXBpLnJlYWQgb2ZmbGluZV9hY2Nlc3MiLCJndHkiOlsicmVmcmVzaF90b2tlbiIsInBhc3N3b3JkIl0sImF6cCI6IkVRdzNmYUF4T1RoUllUWnl5MXVsWkRpOERIUkFZZEVPIn0.QtnB6bbdrJnn9HNFPXJbTRmEKIPUFGAoa3ppYqQjbqw53mE7ePEDsu8hZO1gnNs0_Y4p6UF0Ka2U2lRarXFn-8q5Gv3CXcLetklEqCnWtBdZweZiZDkYzHrjYb7FwjjsBBx8TdhuMrKXSNNnf0zwgKJqjhNVpeMwgt2pUJthdFL8RP8B9rEQvnryQHnMjBo7undtLxbPgLof12tdDAn0p5zDyvmqc_sHjMUaRExTyMYh-lg27A8Yj1dkOug5H8MNQz322ODOOCLpxoPQDlKTA9BJyiEtFWqLQiOYNXw5qNLM0tGiqEvKrClMCjVEQd888kFLasggqaU3vUae1AFfXQ"
def refreshToken():
    global token
    values = '''{
      "apiKey": "QykmTqD-q14dpu7XgD6JpFaIq-3kixcAkhfHL1oktFHTS"
    }'''

    headers = {
        'Content-Type': 'application/json'
    }

    token = requests.post('https://api.swyftx.com.au/auth/refresh/', data=values, headers=headers).json()['accessToken']
    print(token)

def getLatestBar():
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MyApp/1.0'
        }

        response = requests.get(f'https://api.swyftx.com.au/charts/v2/getLatestBar/AUD/{ASSET}/ask/?resolution={RESOLUTION}',
                                headers=headers)


        print(response.status_code)
        print(response.headers)
        print(response.json())

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
        "quantity": QUANTITY,
        "assetQuantity": "AUD",
        "orderType": 1,
    }

    response = requests.post(url, headers=headers, json=payload)
    print("状态码:", response.status_code)
    print("响应内容:", response.json())
    if response.status_code == 401 and response.json()['error']['error'] == 'TokenExpiredError':
        refreshToken()
        buy()

def sell():
    url = "https://api.swyftx.com.au/orders/"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "MyApp/1.0"
    }

    payload = {
        "primary": "AUD",
        "secondary": ASSET,
        "quantity": 0.0004748,
        "assetQuantity": ASSET,
        "orderType": 2,
    }

    response = requests.post(url, headers=headers, json=payload)
    print("状态码:", response.status_code)
    print("响应内容:", response.json())
    if response.status_code == 401 and response.json()['error']['error'] == 'TokenExpiredError':
        refreshToken()
        sell()

buy()