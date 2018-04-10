import ccxt
import threading
from common.model import OrderBook
from common.db import SessionObj


class OrderManager(object):
    def __init__(self, orderbooks: [OrderBook], session: SessionObj):
        self.signal = True
        self.orderbooks = orderbooks
        self.exchanges = [o.exchange for o in self.orderbooks]
        self.pairs = [p.pair for p in self.orderbooks]
        self.session_obj = session
        self.settings = self.session_obj.settings

    class OMThread(threading.Thread):
        def __init__(self, threadNum, asset, window):
            threading.Thread.__init__(self)
            self.threadNum = threadNum
            self.window = window
            self.asset = asset
            self.signal = True

        def run(self):
            while self.signal:
                self.start()
