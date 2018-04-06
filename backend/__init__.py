import logging
import ccxt
# import settings
import time
import configparser
import sys
import os


class BackEnd(object):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.diginet = ccxt.acx({'apiKey': self.config['bot']['diginet_key'],
                                 'secret': self.config['bot']['diginet_secret'],
                                 'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})
        self.bitstamp = ccxt.bitstamp({'apiKey': self.config['bot']['bitstamp_key'],
                                       'secret': self.config['bot']['bitstamp_secret']})

    def get_buy_price_and_quantity(self, orderbook):
        buys = orderbook['asks']
        return buys[0][0], buys[0][1]

    def get_sell_price_and_quantity(self, orderbook):
        sells = orderbook['bids']
        return sells[0][0], sells[0][1]

    def compare_prices(self, bitstamp_orderbook, diginet_oderbook):
        usd_vnd_rate = float(self.config['bot']['usd_vnd_rate'])
        diff_pct = float(self.config['bot']['diff_pct'])
        bitstamp_buy_price, bitstamp_buy_quantity = self.get_buy_price_and_quantity(bitstamp_orderbook)
        bitstamp_sell_price, bitstamp_sell_quantity = self.get_sell_price_and_quantity(bitstamp_orderbook)
        diginet_buy_price, diginet_buy_quantity = self.get_buy_price_and_quantity(diginet_oderbook)
        diginet_sell_price, diginet_sell_quantity = self.get_sell_price_and_quantity(diginet_oderbook)
        self.logger.info('Bitstamp sell price ' + str(bitstamp_sell_price * usd_vnd_rate) +
                         ' - Diginet buy price ' + str(diginet_sell_price) +
                         ' - Diff: ' +
                         str((
                                         bitstamp_sell_price * usd_vnd_rate - diginet_buy_price) / diginet_buy_price * 100) +
                         '%')
        self.logger.info('Diginet sell price ' + str(diginet_sell_price) +
                         ' - Bitstamp buy price ' + str(bitstamp_buy_price * usd_vnd_rate) +
                         ' - Diff: ' +
                         str((
                                         diginet_sell_price / usd_vnd_rate - bitstamp_buy_price) / bitstamp_buy_price * 100) +
                         '%')
        if (bitstamp_sell_price * usd_vnd_rate - diginet_buy_price) / diginet_buy_price > diff_pct:
            self.logger.warning('Buy on diginet ' + str(diginet_buy_price) +
                                ' -> sell on bitstamp ' + str(bitstamp_sell_price * usd_vnd_rate) +
                                ' - Diff: ' +
                                str((
                                                bitstamp_sell_price * usd_vnd_rate - diginet_buy_price) / diginet_buy_price * 100)
                                + '%')
        if (diginet_sell_price / usd_vnd_rate - bitstamp_buy_price) / bitstamp_buy_price > diff_pct:
            self.logger.warning('Buy on bitstamp ' + str(bitstamp_buy_price * usd_vnd_rate) +
                                ' -> sell on diginet ' + str(diginet_sell_price) +
                                ' - Diff: ' +
                                str((
                                                diginet_sell_price / usd_vnd_rate - bitstamp_buy_price) / bitstamp_buy_price * 100)
                                + '%')

    def run_loop(self):
        interval = int(self.config['bot']['interval'])
        while True:
            try:
                diginet_orderbook = self.diginet.fetch_order_book('BTC/VND')
                bitstamp_orderbook = self.bitstamp.fetch_order_book('BTC/USD')
                self.compare_prices(bitstamp_orderbook, diginet_orderbook)
            except Exception as ex:
                logging.error(ex)
            time.sleep(interval)


if __name__ == '__main__':
    BackEnd.run_loop()
