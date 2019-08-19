from cexio_receiver import CexioInterface
from binance_receiver import BinanceInterface
from trade_logger import get_logger
import cexio_keys
import binance_keys
from fractions import Fraction
from orderbook_helper import RtOrderbookWriter
import random
import sys
import threading
import json
import os
from flask import Flask
import os

app = Flask(__name__)

instrument = os.environ.get("INSTRUMENT")
exchanges = os.environ.get("EXCHANGES").split()

interfaces = {'cexio': CexioInterface,
              'binance': BinanceInterface}



def generate_shms(exchanges):
    shm_names = {}
    for exchange in exchanges:
        shm_names[exchange] = '/shm' + str(random.random())
    return shm_names

shm_names = generate_shms(exchanges)

@app.route('/shm')
def hello_world():
    return json.dumps(shm_names)


def launch_feeder(instrument, exchange, shm):
    writer = RtOrderbookWriter(shm)

    keys = {'cexio': cexio_keys.key,
        'binance': binance_keys.key}

    secrets = {'cexio': cexio_keys.secret,
        'binance': binance_keys.secret}

    def display_insert(side, quantity, price):
        print("Inserting from {} {}: {}@{}".format(exchange, side, quantity, price))
        writer.set_quantity_at(side, *quantity.as_integer_ratio(), *price.as_integer_ratio())

    def reset_orderbook():
        writer.reset_content()

    cexio_logger = get_logger('Man Trade', 'mantrader.log')
    iface = interfaces[exchange](instrument, keys[exchange], secrets[exchange], cexio_logger, subscriptions=["orderbook"], on_orderbook_update=display_insert, on_ignite=reset_orderbook)
    print("Starting up interface!")
    iface.startup()


print('SHM paths are', str(shm_names.values()))

for exchange, shm_name in shm_names.items():
    p = threading.Thread(target=launch_feeder, args=(instrument, exchange, shm_name))
    p.start()


print("Started all orderbooks!")

