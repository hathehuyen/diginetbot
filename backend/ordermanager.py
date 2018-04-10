import ccxt
import threading
from common.model import OrderBook
from common.db import SessionObj


class diginet(ccxt.acx):
    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        order = {
            'market': self.market_id(symbol),
            'side': side,
            'volume': str(amount),
            'ord_type': type,
        }
        if type == 'limit':
            order['price'] = str(price)
        response = self.privatePostOrders(self.extend(order, params))
        market = self.markets_by_id[response['market']]
        return self.parse_order(response, market)


class OrderManager(object):
    def __init__(self, bitstamp_orderbook: OrderBook, diginet_orderbook: OrderBook, session: SessionObj):
        self.signal = True
        self.bitstamp_orderbook = bitstamp_orderbook
        self.diginet_orderbook = diginet_orderbook
        self.exchanges = []
        self.session_obj = session
        self.settings = self.session_obj.settings
        self.bitstamp_exchanger = ccxt.bitstamp({'apiKey': self.settings['bitstamp']['key'],
                                                 'secret': self.settings['bitstamp']['secret'],
                                                 'uid': self.settings['bitstamp']['uid']})
        self.diginet_exchanger = ccxt.acx({'apiKey': self.settings['diginet']['key'],
                                           'secret': self.settings['diginet']['secret'],
                                           'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})

    def fetch_balance(self):
        self.diginet_exchanger.balance = self.diginet_exchanger.fetch_balance()
        self.bitstamp_exchanger.balance = self.bitstamp_exchanger.fetch_balance()
        # print(self.diginet_exchanger.balance['VND']['free'])

    def get_order_status(self):
        self.diginet_exchanger.orders = self.diginet_exchanger.create_order()
        print(self.diginet_exchanger.orders)

    def get_bitstamp_oder(self):
        bitstamp_order = {}
        for orderbook in self.orderbooks:
            if orderbook.exchange == 'bitstamp':
                bitstamp_order = orderbook
        bitstamp_asks = bitstamp_order.asks
        bitstamp_bids = bitstamp_order.bids
        return bitstamp_asks, bitstamp_bids

    def generate_diginet_orders(self, bitstamp_asks, bitstamp_bids):
        bid_orders = []
        ask_orders = []
        for i in range(0, int(self.settings['bitstamp']['order_to_copy']) - 1):
            # Generate bid orders from asks
            price = bitstamp_asks[i][0] * int(self.settings['diginet']['usd_vnd_rate']) + \
                    (bitstamp_asks[i][0] * int(self.settings['diginet']['usd_vnd_rate']) *
                     int(self.settings['bitstamp']['diff_pct']))
            volume: float = 0
            if bitstamp_asks[i][1] < self.settings['bitstamp']['']:
                volume = bitstamp_asks[i][1] * self.settings['bitstamp']['order_pct']
            bid_orders.append([price, volume])

            # Generate ask orders from bids
            price = bitstamp_bids[i][0] * int(self.settings['diginet']['usd_vnd_rate']) - \
                    (bitstamp_bids[i][0] * int(self.settings['diginet']['usd_vnd_rate']) *
                     int(self.settings['bitstamp']['diff_pct']))
            volume: float = 0
            if bitstamp_asks[i][1] < self.settings['bitstamp']['']:
                volume = bitstamp_asks[i][1] * self.settings['bitstamp']['order_pct']
            bid_orders.append([price, volume])
        return ask_orders, bid_orders

    def place_diginet_orders(self, ask_orders, bid_orders):
        for ask_order in ask_orders:
            self.diginet_exchanger.create_order('BTC/VND', 'limit', 'buy', ask_order[0], ask_order[1])
        for bid_order in bid_orders:
            self.diginet_exchanger.create_order('BTC/VND', 'limit', 'sell', bid_order[0], bid_order[1])

    def run(self):
        self.fetch_balance()
        ask_orders, bid_orders = self.generate_diginet_orders()
        self.place_diginet_orders(ask_orders, bid_orders)

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
