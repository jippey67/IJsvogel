from binance.websockets import BinanceSocketManager
from binance.client import Client
import keys
import ssl
import urllib.request
import json
client = Client(keys.api_key, keys.api_secret, {"verify": False, "timeout": 20})

def process_message(msg):


    usdt = float(msg.get('p'))
    bitcoin = json.loads(urllib.request.urlopen(url, context=context).read()).get("USD")
    calc = bitcoin/usdt
    print('1 USDT is', calc, 'USD. BTC:', bitcoin, 'USDT:', usdt)

    #print(msg)
    # do something

context = ssl._create_unverified_context()
url = 'https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD&api_key={3d61edda26c698f29ca05ad2e6f5f5dccc10b2b25a41fce0bd9eafa951166110}'

bm = BinanceSocketManager(client)
# start any sockets here, i.e a trade socket
conn_key = bm.start_trade_socket('BTCUSDT', process_message)
# then start the socket manager
bm.start()





