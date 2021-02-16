import time
import datetime
import gzip
import posix_ipc
from pprint import pprint
import threading
import umsgpack
from peewee import *
from decimal import Decimal
from universal_listenner import UniversalFeedListenner

db = SqliteDatabase('people.db')

class OrderbookEntryUpdate(Model):
    side = CharField()
    base = CharField()
    quote = CharField()
    exchange = CharField()
    timestamp = DateTimeField()
    price = DecimalField()
    size = DecimalField()

    class Meta:
        database = db # This model uses the "people.db" database.

def loggit(*args):
    print("{}: ".format(datetime.datetime.now()), *args)

class Listenner(UniversalFeedListenner):
    def __init__(self, addr, port, exchange, market, record=False, record_time=10, buffer_length=100, record_path='./'):
        super().__init__(addr, port, exchange, market, 'orderbook', on_receive=self.receive_fn)
        self.saving = False
        self.write_thread = None
        self.messages_sem = posix_ipc.Semaphore(None, posix_ipc.O_CREX, initial_value=1)
        self.record, self.record_path = record, record_path
        self.record_time, self.buffer_length = record_time, buffer_length
        self.startup_time = None
        self.messages = []


    def receive_fn(self, message):
        self.startup_time = time.time()*1000 if self.startup_time is None else self.startup_time
        delta_time = message["server_received"] - self.startup_time
        # print("Delta time", delta_time, 'startup', self.startup_time, 'received', message["server_received"])
        self.save_or_ditch(message, delta_time)
        if self.record: self.watch_time(delta_time) 


    def should_write(self, delta_time):
        with self.messages_sem:
            non_empty = len(self.messages) > 0
            recording = (self.record and ((self.record_time > 0) and (delta_time > self.record_time)) and not self.finish)
            result = (non_empty and (len(self.messages) >= self.buffer_length or recording))
            return result


    def save_or_ditch(self, message, elapsed_time):
        if self.record and ((elapsed_time <= self.record_time) or self.record_time <= 0):
            #pprint(message)
            with self.messages_sem:
                self.messages.append(message)
        if self.should_write(elapsed_time):
            if self.write_thread: self.write_thread.join()
            self.write_thread = threading.Thread(target=self.write_to_disk)
            self.write_thread.start()


    def write_to_disk(self):
        self.saving = True
        with self.messages_sem:
            log_message = "Saving to file messages of length {}...".format(len(self.messages))
            loggit(log_message)
            # packed = umsgpack.dumps(self.messages)
            for mes in self.messages:
                base = mes['base']
                quote = mes['quote']
                timestamp = datetime.datetime.fromtimestamp(mes['timestampMs']/1000)
                exchange = mes['exchange']
                for upd in mes['asks']:
                    obentry = OrderbookEntryUpdate(side='ask', price=Decimal(upd['price']), size=Decimal(upd['size']), timestamp=timestamp, base=base, quote=quote, exchange=exchange)
                    obentry.save()
                for upd in mes['bids']:
                    obentry = OrderbookEntryUpdate(side='bid', price=Decimal(upd['price']), size=Decimal(upd['size']), timestamp=timestamp, base=base, quote=quote, exchange=exchange)
                    obentry.save()
            self.messages = []
        #with gzip.open('{}/{}.gz'.format(self.record_path, time.time()), 'wb') as outfile:
        #    outfile.write(packed)
            
        self.saving = False


    def watch_time(self, elapsed_time):
        if self.record_time and elapsed_time > self.record_time:
            while self.saving:
                pass
            self.record = False
            loggit("Finished recording")


if __name__ == "__main__":
    market = {
        "id": "BTC/USD",
        "base": "BTC",
        "quote": "USD",
    }

    listenner = Listenner('127.0.0.1', '4242', 'FTX', market, record=True, record_time=100000, buffer_length=10, record_path='./')
    listenner.run()