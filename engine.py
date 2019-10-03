from binance.websockets import BinanceSocketManager
from binance.client import Client
from binance.enums import *

import ssl
import urllib.request
import json
import datetime

import mailer
import specifications

debug = True

triggerHi = 1 + specifications.targetTrigger
triggerLo = 1 - specifications.targetTrigger
orderSpace = specifications.orderSpace

class Robot:
    def __init__(self):
        self.client = Client(specifications.api_key_p, specifications.api_secret_p, {"verify": False, "timeout": 20})
        self.bm = BinanceSocketManager(self.client)
        self.bm.start_trade_socket('BTCUSDT', self.market_event)
        self.bm.start_user_socket(self.user_event)
        self.bm.start()

        BTCbalance = float(self.client.get_asset_balance(asset='BTC')['free'])
        USDTbalance = float(self.client.get_asset_balance(asset='USDT')['free'])
        rate = float(self.client.get_order_book(symbol='BTCUSDT')['bids'][0][0])

        self.position = 'FLAT'
        if (rate*BTCbalance / USDTbalance) > 5:
            self.position = 'BITCOIN'
        if (rate*BTCbalance / USDTbalance) < 0.2:
            self.position = 'TETHER'
        print(self.position)

        self.bitcoin = 8000  # initial value in case first trial results in error

        self.orderStatus = ''
        self.orderId = ''
        self.NoOrderInProgress = True  # prevent multiple orders due to exchange latency

    def getBTCquote(self, oldQuote):
        context = ssl._create_unverified_context()
        url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD&api_key={3d61edda26c698f29ca05ad2e6f5f5dccc10b2b25a41fce0bd9eafa951166110}'
        try:
            btcusd = json.loads(urllib.request.urlopen(url, context=context).read()).get("USD")
            return btcusd
        except Exception as e:
            if debug:
                print('No btcusd quote obtained', e)
            return oldQuote

    def order(self, orderDetails):
        type = orderDetails[0]
        quantity = orderDetails[1]
        limitPrice = orderDetails[2]
        precision = 8
        price_string = '{:0.0{}f}'.format(limitPrice, precision)

        if type == 'buy':
            order = self.client.order_limit_buy(symbol='BTCUSDT', quantity=quantity, price=price_string)
            self.orderId = order['orderId']
            self.orderStatus = order['status']
            self.logOrders('buy initiated, order:'+self.orderId)

        if type == 'sell':
            order = self.client.order_limit_sell(symbol='BTCUSDT', quantity=quantity, price=price_string)
            self.orderId = order['orderId']
            self.orderStatus = order['status']
            self.logOrders('sell initiated, order:' + self.orderId)

    def user_event(self, msg):
        if msg['e'] == 'executionReport':
            if msg['x'] == 'TRADE':
                self.logOrders('order filled: '+msg['i'])
                self.NoOrderInProgress = True
                mailer.mailer('order filled: '+msg['i'])

    def market_event(self, msg):
        usdt = float(msg.get('p'))
        self.bitcoin = self.getBTCquote(self.bitcoin)
        rate = self.bitcoin / usdt
        if debug: print('1 USDT is', '{:10.8f}'.format(rate))
        if self.NoOrderInProgress:
            if self.position == 'FLAT':
                if rate > triggerHi:
                    limitPrice = self.bitcoin*(1+orderSpace)
                    quantity = float(self.client.get_asset_balance(asset='BTC')['free'])
                    self.NoOrderInProgress = False
                    self.order(['buy', quantity, limitPrice])
                if rate > triggerLo:
                    limitPrice = self.bitcoin * (1 - orderSpace)
                    quantity = float(self.client.get_asset_balance(asset='USDT')['free'])/limitPrice
                    self.NoOrderInProgress = False
                    self.order(['sell', quantity, limitPrice])
            if self.position == 'BITCOIN':
                if rate < 1:
                    limitPrice = self.bitcoin * (1 - orderSpace)
                    quantity = 0.5 * float(self.client.get_asset_balance(asset='BTC')['free'])
                    self.NoOrderInProgress = False
                    self.order(['sell', quantity, limitPrice])
            if self.position == 'TETHER':
                if rate > 1:
                    limitPrice = self.bitcoin * (1 + orderSpace)
                    quantity = 0.5 * float(self.client.get_asset_balance(asset='USDT')['free'])/limitPrice
                    self.NoOrderInProgress = False
                    self.order(['buy', quantity, limitPrice])


    def logOrders(self, payload):
        with open("ordersLog.txt","a+") as file:
            file.write(str(datetime.datetime.utcnow())+" "+str(payload)+"\n")

bot = Robot()



