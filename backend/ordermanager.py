import logging
import ccxt
import time
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
        self.logger = logging.getLogger(__name__)
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
        diginet_vnd_free = float(self.diginet_exchanger.balance['VND']['free']) * \
                           float(self.settings['diginet']['currency_max_pct'])
        diginet_btc_free = float(self.diginet_exchanger.balance['BTC']['free']) * \
                           float(self.settings['diginet']['asset_max_pct'])
        bitstamp_usd_free = float(self.bitstamp_exchanger.balance['USD']['free']) * \
                            float(self.settings['bitstamp']['currency_max_pct'])
        bitstamp_btc_free = float(self.bitstamp_exchanger.balance['BTC']['free']) * \
                            float(self.settings['bitstamp']['asset_max_pct'])
        self.logger.info('Diginet balance (btc/vnd): ' + str(diginet_btc_free) + '/' + str(diginet_vnd_free))
        self.logger.info('Bitstamp balance (btc/usd): ' + str(bitstamp_btc_free) + '/' + str(bitstamp_usd_free))
        for i in range(0, int(self.settings['bitstamp']['order_to_copy']) - 1):
            # check balance
            if bitstamp_btc_free <= 0 or diginet_vnd_free <= 0:
                break
            # Generate bid orders from asks
            # Buy from diginet, sell on bitstamp
            price = bitstamp_asks[i][0] * float(self.settings['diginet']['usd_vnd_rate']) + \
                    (bitstamp_asks[i][0] * float(self.settings['diginet']['usd_vnd_rate']) *
                     float(self.settings['bitstamp']['diff_pct']))
            if bitstamp_asks[i][1] < float(self.settings['bitstamp']['btc_vnd_max']):
                volume = bitstamp_asks[i][1] * float(self.settings['bitstamp']['order_pct'])
            else:
                volume = float(self.settings['bitstamp']['btc_vnd_max'])
            if volume > bitstamp_btc_free:
                volume = bitstamp_btc_free
            if volume * price > diginet_vnd_free:
                volume = diginet_vnd_free / price
            if not (bitstamp_asks[i][0] * volume < float(self.settings['bitstamp']['min_order']) or
                    price * volume < float(self.settings['diginet']['min_order'])):
                bid_orders.append([price, volume])
                bitstamp_btc_free -= volume
                diginet_vnd_free -= volume * price

        for i in range(0, int(self.settings['bitstamp']['order_to_copy']) - 1):
            # Check balance
            if bitstamp_usd_free <= 0 or diginet_btc_free <= 0:
                break
            # Generate ask orders from bids
            # Buy from bitstamp, sell on diginet
            price = bitstamp_bids[i][0] * float(self.settings['diginet']['usd_vnd_rate']) - \
                    (bitstamp_bids[i][0] * float(self.settings['diginet']['usd_vnd_rate']) *
                     float(self.settings['bitstamp']['diff_pct']))
            volume = bitstamp_asks[i][1] * float(self.settings['bitstamp']['order_pct'])
            if volume > bitstamp_usd_free * bitstamp_bids[i][0]:
                volume = bitstamp_usd_free * bitstamp_bids[i][0]
            if volume > diginet_btc_free:
                volume = diginet_btc_free
            if not (bitstamp_bids[i][0] * volume < float(self.settings['bitstamp']['min_order']) or
                    price * volume < float(self.settings['diginet']['min_order'])):
                ask_orders.append([price, volume])
                diginet_btc_free -= volume
                bitstamp_usd_free -= volume * bitstamp_bids[i][0]

        return ask_orders, bid_orders

    def place_diginet_orders(self, ask_orders, bid_orders):
        for ask_order in ask_orders:
            self.logger.info('Buy ' + str(ask_order[1]) + '@' + str(ask_order[1]))
            # self.diginet_exchanger.create_order('BTC/VND', 'limit', 'buy', ask_order[1], ask_order[0])
        for bid_order in bid_orders:
            self.logger.info('Buy ' + str(bid_order[1]) + '@' + str(bid_order[1]))
            # self.diginet_exchanger.create_order('BTC/VND', 'limit', 'sell', bid_order[1], bid_order[0])

    def run_loop(self):
        while self.signal:
            try:
                self.logger.info('Update balance')
                self.fetch_balance()
                self.logger.info('Generate orders from bitstamp order book')
                ask_orders, bid_orders = self.generate_diginet_orders(self.bitstamp_orderbook.asks, self.bitstamp_orderbook.bids)
                # self.logger.info(str(ask_orders))
                # self.logger.info(str(bid_orders))
                self.logger.info('Place diginet order')
                self.place_diginet_orders(ask_orders, bid_orders)
            except Exception as ex:
                print(ex)
            time.sleep(int(self.settings['bot']['interval']))

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

    def run_thread(self):
        thread = threading.Thread(target=lambda: self.run_loop())
        thread.daemon = True
        thread.start()
