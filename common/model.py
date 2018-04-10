import logging
import threading
import ccxt
import time


class OrderBook(object):
    def __init__(self, exchange: str='bitstamp', pair: str='BTC/USD', logger=None):
        self.exchange = exchange
        self.pair = pair
        self.logger = logger or logging.getLogger(__name__)
        if self.exchange == 'bitstamp':
            self.source = ccxt.bitstamp()
        elif self.exchange == 'diginet':
            self.source = ccxt.acx({'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})
        else:
            raise ValueError('Exchange not supported!')
        self.asks = []
        self.bids = []
        self.last_update: float = 0
        self.update_thread = None

    def get_buy_price_and_quantity(self, orderbook):
        buys = orderbook['asks']
        return buys[0][0], buys[0][1]

    def get_sell_price_and_quantity(self, orderbook):
        sells = orderbook['bids']
        return sells[0][0], sells[0][1]

    def run_loop(self):
        interval: int = 5
        while True:
            try:
                orderbook = self.source.fetch_order_book(self.pair)
                self.asks = orderbook['ask']
                self.bids = orderbook['bids']
                self.last_update = time.time()
            except Exception as ex:
                logging.error(ex)
            time.sleep(interval)

    def start(self):
        self.update_thread = threading.Thread(target=lambda: self.run_loop())
        self.update_thread.daemon = True
        self.update_thread.start()
        self.logger.info('Order book thread started: ' + self.exchange + '-' + self.pair)

