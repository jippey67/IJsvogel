from binance.websockets import BinanceSocketManager
from binance.client import Client
import keys
import ssl
import urllib.request
import json


#global minPrice, maxPrice
minPrice = 1
maxPrice = 1

def process_message(msg):
    global minPrice
    global maxPrice
    usdt = float(msg.get('p'))
    bitcoin = json.loads(urllib.request.urlopen(url, context=context).read()).get("USD")
    calc = bitcoin/usdt
    minPrice = min(minPrice, calc)
    maxPrice = max(maxPrice, calc)
    print('1 USDT is', '{:10.8f}'.format(calc), 'USD. max is', '{:6.4f}'.format((maxPrice-1)*100),'% min is', '{:6.4f}'.format((minPrice-1)*100), '% spread is','{:6.4f}'.format((maxPrice-minPrice)*100), '%')

client = Client(keys.api_key, keys.api_secret, {"verify": False, "timeout": 20})

context = ssl._create_unverified_context()
url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD&api_key={3d61edda26c698f29ca05ad2e6f5f5dccc10b2b25a41fce0bd9eafa951166110}'

bm = BinanceSocketManager(client)
# start any sockets here, i.e a trade socket
conn_key = bm.start_trade_socket('BTCUSDT', process_message)
# then start the socket manager
bm.start()





