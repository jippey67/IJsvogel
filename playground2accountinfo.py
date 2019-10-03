from binance.websockets import BinanceSocketManager
from binance.client import Client
from binance.enums import *
import specifications
import ssl
import urllib.request
import json


client = Client(specifications.api_key_p, specifications.api_secret_p, {"verify": False, "timeout": 20})

tickers = client.get_orderbook_tickers()
print(tickers)

precision = 8
price = 5000
price_string = '{:0.0{}f}'.format(price, precision)
print(price_string)
order = client.order_limit_buy(
    symbol='BTCUSDT',
    quantity=0.002,
    price=price_string)
print(order)

orderId = order['orderId']
orderStat = order['status']
print(orderId, orderStat)

'''
order = client.create_test_order(
    symbol='ETHBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price=price_string)

print(order)
'''
'''

info = client.get_account()
print(info)
balance = client.get_asset_balance(asset='BTC')
print(balance)
balance = client.get_asset_balance(asset='USDT')
print(balance)
details = client.get_asset_details()
print(details)
depth = client.get_order_book(symbol='BTCUSDT')
koers = depth['bids'][0][0]
print(depth)
print(koers)
orders = client.get_open_orders(symbol='BTCUSDT')
print(orders)
'''