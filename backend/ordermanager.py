import logging
import ccxt
import time
import threading
from common.model import OrderBook
from common.db import SessionObj, LogObj


class diginet(ccxt.acx):
    """
    Diginet exchange implement
    """
    def get_order(self, id, symbol=None, params={}):
        """
        Get order status by id
        :param id: order id (required)
        :param symbol:
        :param params:
        :return:
        """
        self.load_markets()
        result = self.privateGetOrder({'id': id})
        order = self.parse_order(result)
        # status = order['status']
        # if status == 'closed' or status == 'canceled':
        #     raise OrderNotFound(self.id + ' ' + self.json(order))
        return order

    def cancel_all_order(self, symbol=None, params={}):
        """
        Cancel all active order
        :param symbol:
        :param params:
        :return:
        """
        self.load_markets()
        result = self.privatePostOrdersClear()
        # order = self.parse_order(result)
        # status = order['status']
        # if status == 'closed' or status == 'canceled':
        #     raise OrderNotFound(self.id + ' ' + self.json(order))
        return result


class OrderManager(object):
    """
    Order manager object maintain order book on diginet exchange by copying from bitstamp exchange order book
    """
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
        self.diginet_exchanger = diginet({'apiKey': self.settings['diginet']['key'],
                                           'secret': self.settings['diginet']['secret'],
                                           'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})

    def save_log_obj(self, text: str=''):
        """
        Save log to database
        :param text: text to log
        :return: log object's id
        """
        log_obj = LogObj()
        log_obj.user_id = self.session_obj.user_id
        log_obj.session_id = self.session_obj.id
        log_obj.text = text
        return log_obj.save()

    def fetch_balance(self):
        """
        Updae balance
        :return:
        """
        self.save_log_obj('Update balance')
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
        """
        Generate orders to place on diginet exchange from bitstamp order book
        :param bitstamp_asks: bitstamp's order book asks
        :param bitstamp_bids: bitstamp's order book bids
        :return: Orders to place on diginet exchange [[price, volume]]
        """
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
            if diginet_vnd_free <= float(self.settings['diginet']['min_order']):
                break
            # Buy from diginet, sell on bitstamp
            price = bitstamp_asks[i][0] * float(self.settings['diginet']['usd_vnd_rate']) - \
                    (bitstamp_asks[i][0] * float(self.settings['diginet']['usd_vnd_rate']) *
                     float(self.settings['bitstamp']['diff_pct']))
            volume = bitstamp_asks[i][1] * float(self.settings['bitstamp']['orderbook_pct'])
            if volume * price > float(self.settings['diginet']['vnd_btc_max']):
                volume = float(self.settings['diginet']['vnd_btc_max']) / price
            if volume > bitstamp_btc_free:
                volume = bitstamp_btc_free
            if volume * price > diginet_vnd_free:
                volume = diginet_vnd_free / price
            # self.logger.info('Price ' + str(price) + ' - Volume ' + str(volume))
            if not (bitstamp_asks[i][0] * volume < float(self.settings['bitstamp']['min_order']) or
                    price * volume < float(self.settings['diginet']['min_order'])):
                ask_orders.append([price, volume])
                bitstamp_btc_free -= volume
                diginet_vnd_free -= volume * price

        for i in range(0, int(self.settings['bitstamp']['order_to_copy']) - 1):
            # Check balance
            if bitstamp_usd_free <= float(self.settings['bitstamp']['min_order']):
                break
            # Generate bids orders from bids
            # Buy from bitstamp, sell on diginet
            price = bitstamp_bids[i][0] * float(self.settings['diginet']['usd_vnd_rate']) + \
                    (bitstamp_bids[i][0] * float(self.settings['diginet']['usd_vnd_rate']) *
                     float(self.settings['bitstamp']['diff_pct']))
            volume = bitstamp_bids[i][1] * float(self.settings['bitstamp']['orderbook_pct'])
            if volume > bitstamp_usd_free / bitstamp_bids[i][0]:
                volume = bitstamp_usd_free / bitstamp_bids[i][0]
            if volume > diginet_btc_free:
                volume = diginet_btc_free
            # self.logger.info('Price ' + str(price) + ' - Volume ' + str(volume))
            if not (bitstamp_bids[i][0] * volume < float(self.settings['bitstamp']['min_order']) or
                    price * volume < float(self.settings['diginet']['min_order'])):
                bid_orders.append([price, volume])
                diginet_btc_free -= volume
                bitstamp_usd_free -= volume * bitstamp_bids[i][0]

        return ask_orders, bid_orders

    def test_diginet_orders(self):
        self.logger.info('Test diginet order')
        # order = self.diginet_exchanger.create_order('BTC/VND', 'limit', 'sell', 0.0001, 200000000)
        # self.logger.info(str(order))
        # time.sleep(10)
        # self.logger.info('Cancel order')
        # status = self.diginet_exchanger.cancel_order(order['id'], order['symbol'])
        status = self.diginet_exchanger.get_order('25809098', 'BTC/VND')
        self.logger.info(str(status))

    def place_diginet_orders(self, ask_orders, bid_orders):
        """
        Place orders on diginet exchange
        :param ask_orders: ask orders [[price, volume]]
        :param bid_orders: bid orders [[price, volume]]
        :return: List of orders placed
        """
        orders = []
        if ask_orders or bid_orders:
            self.save_log_obj('Place diginet orders')
        for ask_order in ask_orders:
            self.logger.info('Buy ' + str(ask_order[1]) + '@' + str(ask_order[0]))
            self.save_log_obj('Buy ' + str(ask_order[1]) + '@' + str(ask_order[0]))
            order = self.diginet_exchanger.create_order('BTC/VND', 'limit', 'buy', ask_order[1], ask_order[0])
            orders.append(order)
        for bid_order in bid_orders:
            self.logger.info('Buy ' + str(bid_order[1]) + '@' + str(bid_order[0]))
            self.save_log_obj('Buy ' + str(bid_order[1]) + '@' + str(bid_order[0]))
            order = self.diginet_exchanger.create_order('BTC/VND', 'limit', 'sell', bid_order[1], bid_order[0])
            orders.append(order)
        return orders

    def run_loop(self):
        """
        The main loop
        :return:
        """
        self.logger.info('Cancel all diginet orders')
        self.save_log_obj('Cancel all diginet orders')
        self.diginet_exchanger.cancel_all_order()
        while self.signal:
            orders = []
            try:
                self.logger.info('Update balance')
                self.fetch_balance()
                self.logger.info('Generate orders from bitstamp order book')
                ask_orders, bid_orders = self.generate_diginet_orders(self.bitstamp_orderbook.asks, self.bitstamp_orderbook.bids)
                self.logger.info('Place diginet order')
                orders = self.place_diginet_orders(ask_orders, bid_orders)
                # self.test_diginet_orders()
            except Exception as ex:
                self.logger.error(str(ex))
            time.sleep(int(self.settings['bot']['interval']))
            try:
                if orders:
                    self.logger.info('Check orders status')
                    self.save_log_obj('Check orders status')
                    for order in orders:
                        order = self.diginet_exchanger.get_order(order['id'])
                        self.logger.info(str(order))
                        self.save_log_obj(str(order))
                        if order['status'] == 'open':
                            self.logger.info('Close order id ' + order['id'])
                            self.save_log_obj('Close order id ' + order['id'])
                            self.diginet_exchanger.cancel_order(order['id'])
                        if order['status'] == 'closed':
                            self.logger.info('Order ' + order['id'] + ' filled, place market order on bitstamp')
                            self.save_log_obj('Order ' + order['id'] + ' filled, place market order on bitstamp')
                            if order['side'] == 'sell':
                                self.logger.info('Sell ' + str(order['filled']) + 'BTC on bitstamp')
                                self.save_log_obj('Sell ' + str(order['filled']) + 'BTC on bitstamp')
                                self.bitstamp_exchanger.create_market_buy_order('BTC/USD', order['filled'])
                            if order['side'] == 'buy':
                                self.logger.info('Buy ' + str(order['filled']) + 'BTC on bitstamp')
                                self.save_log_obj('Buy ' + str(order['filled']) + 'BTC on bitstamp')
                                self.bitstamp_exchanger.create_market_sell_order('BTC/USD', order['filled'])
                else:
                    self.logger.info('No active orders on diginet')
                    self.save_log_obj('No active orders on diginet')
            except Exception as ex:
                self.logger.error(str(ex))
                self.save_log_obj(str(ex))
        self.logger.info('Cancel all diginet orders')
        self.save_log_obj('Cancel all diginet orders')
        self.diginet_exchanger.cancel_all_order()

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
        """
        Run main loop as threading
        :return:
        """
        thread = threading.Thread(target=lambda: self.run_loop())
        thread.daemon = True
        thread.start()
        self.save_log_obj('Bot started for user ' + str(self.session_obj.user_id))
