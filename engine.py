from binance.websockets import BinanceSocketManager
from binance.client import Client
from bitfinex import WssClient, ClientV2, ClientV1

import ssl
import urllib.request
import json
import datetime
import urllib3


import mailer
from simplecrypt import decrypt
from getpass import getpass

debug = True
test = True
production = not test
urllib3.disable_warnings()

with open('specs.cfg', 'rb') as file:
    specsString = file.read()
pw = getpass()
unencodedString = decrypt(pw, specsString)
specifications = eval(unencodedString)

now = datetime.datetime.now()
dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
quoteLog = 'quotes'+dt_string+'.csv'

if test:
    triggerHi = 1 + 0.001
    triggerLo = 1 - 0.001
    orderSpace = specifications['orderSpace']
if production:
    triggerHi = 1 + specifications['targetTrigger']
    triggerLo = 1 - specifications['targetTrigger']
    orderSpace = specifications['orderSpace']

class Robot:
    def __init__(self):
        self.bitcoin = None
        self.orderStatus = ''
        self.orderId = ''
        self.noOrderInProgress = True  # prevent multiple orders due to exchange latency
        self.nextPosition = ''

        self.startSockets()

        BTCbalance = float(self.client.get_asset_balance(asset='BTC')['free'])
        USDTbalance = float(self.client.get_asset_balance(asset='USDT')['free'])
        rate = float(self.client.get_order_book(symbol='BTCUSDT')['bids'][0][0])

        self.position = 'FLAT'
        if (rate*BTCbalance / USDTbalance) > 5:
            self.position = 'BITCOIN'
        if (rate*BTCbalance / USDTbalance) < 0.2:
            self.position = 'TETHER'
        print(self.position)





    def startSockets(self):
        self.client = Client(specifications['api_key_p'], specifications['api_secret_p'], {"verify": False, "timeout": 20})
        self.bm = BinanceSocketManager(self.client)
        self.bm.start_trade_socket('BTCUSDT', self.market_event)
        self.bm.start_user_socket(self.user_event)
        self.bm.start()

        self.bitfinex_client = WssClient()
        self.bitfinex_client.subscribe_to_ticker(symbol="BTCUSD", callback=self.bitfinex_event)
        self.bitfinex_client.start()

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

    def bitfinex_event(self, msg):
        if isinstance(msg, list):
            if isinstance(msg[1][0], int) or isinstance(msg[1][0], float):
                self.bitcoin = float(msg[1][0])

    def user_event(self, msg):
        if msg['e'] == 'executionReport':
            if msg['x'] == 'TRADE':
                self.logOrders('order filled: '+msg['i'])
                self.noOrderInProgress = True
                mailer.mailer(specifications['mail_a'], specifications['mail_p'], 'order filled: '+msg['i'])
                self.position = self.nextPosition

    def testOrder(self, rate, action, tetP, btcP, limitPrice, quantity, nextPosition):
        self.position = nextPosition
        logString = action + ' ' + str(rate) + ', tether: ' + str(tetP) + ', bitcoin: ' +str(btcP) + ', limit: ' + str(limitPrice) + ', quantity: ' + str(quantity) + ', position: ' + nextPosition
        self.logOrders(logString)
        self.noOrderInProgress = True

    def market_event(self, msg):
        usdt = float(msg.get('p'))
        if self.noOrderInProgress and (self.bitcoin is not None):
            rate = self.bitcoin / usdt
            if self.position == 'FLAT':
                if rate > triggerHi:
                    limitPrice = self.bitcoin*(1+orderSpace)
                    quantity = float(self.client.get_asset_balance(asset='BTC')['free'])
                    self.NoOrderInProgress = False
                    self.nextPosition = 'BITCOIN'
                    buySell = 'buy'
                    if production: self.order([buySell, quantity, limitPrice])
                    if test: self.testOrder(rate, buySell, usdt, self.bitcoin, limitPrice, quantity, self.nextPosition)
                if rate < triggerLo:
                    limitPrice = self.bitcoin * (1 - orderSpace)
                    quantity = float(self.client.get_asset_balance(asset='USDT')['free'])/limitPrice
                    self.NoOrderInProgress = False
                    self.nextPosition = 'TETHER'
                    buySell = 'sell'
                    if production: self.order([buySell, quantity, limitPrice])
                    if test: self.testOrder(rate, buySell, usdt, self.bitcoin, limitPrice, quantity, self.nextPosition)
            if self.position == 'BITCOIN':
                if rate < 1:
                    limitPrice = self.bitcoin * (1 - orderSpace)
                    quantity = 0.5 * float(self.client.get_asset_balance(asset='BTC')['free'])
                    self.NoOrderInProgress = False
                    self.nextPosition = 'FLAT'
                    buySell = 'sell'
                    if production: self.order([buySell, quantity, limitPrice])
                    if test: self.testOrder(rate, buySell, usdt, self.bitcoin, limitPrice, quantity, self.nextPosition)
            if self.position == 'TETHER':
                if rate > 1:
                    limitPrice = self.bitcoin * (1 + orderSpace)
                    quantity = 0.5 * float(self.client.get_asset_balance(asset='USDT')['free'])/limitPrice
                    self.NoOrderInProgress = False
                    self.nextPosition = 'FLAT'
                    buySell = 'buy'
                    if production: self.order([buySell, quantity, limitPrice])
            if test: print('tether:', usdt, 'bitcoin:', self.bitcoin, '1 USDT is', '{:10.8f}'.format(rate), 'USD. market position:', self.position)
            if test: self.logQuotes(rate)

    def logOrders(self, payload):
        with open("ordersLog.txt","a+") as file:
            file.write(str(datetime.datetime.utcnow())+" "+str(payload)+"\n")

    def logQuotes(self, payload):
        with open(quoteLog, 'a') as file:
            file.write(str(datetime.datetime.utcnow())+","+str(payload)+"\n")

bot = Robot()



