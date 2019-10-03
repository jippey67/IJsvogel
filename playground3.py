from binance.websockets import BinanceSocketManager
from binance.client import Client
from binance.enums import *
import specifications
import ssl
import urllib.request
import json


#global minPrice, maxPrice
minPrice = 1
maxPrice = 1

def process_message(msg):
    print(msg)

client = Client(specifications.api_key_p, specifications.api_secret_p, {"verify": False, "timeout": 20})


bm = BinanceSocketManager(client)
# start any sockets here, i.e a trade socket
conn_key = bm.start_user_socket(process_message)
# then start the socket manager
bm.start()





