import ccxt
import settings
import logging
import time

# set logging time to GMT
logging.Formatter.converter = time.gmtime
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

diginet = ccxt.acx({'apiKey': settings.diginet_key, 'secret': settings.diginet_secret,
                    'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})
bitstamp = ccxt.bitstamp({'apiKey': settings.bitstamp_key, 'secret': settings.bitstamp_secret})


def get_buy_price_and_quantity(orderbook):
    buys = orderbook['asks']
    return buys[0][0], buys[0][1]


def get_sell_price_and_quantity(orderbook):
    sells = orderbook['bids']
    return sells[0][0], sells[0][1]


def compare_prices(bitstamp_orderbook, diginet_oderbook):
    bitstamp_buy_price, bitstamp_buy_quantity = get_buy_price_and_quantity(bitstamp_orderbook)
    bitstamp_sell_price, bitstamp_sell_quantity = get_sell_price_and_quantity(bitstamp_orderbook)
    diginet_buy_price, diginet_buy_quantity = get_buy_price_and_quantity(diginet_oderbook)
    diginet_sell_price, diginet_sell_quantity = get_sell_price_and_quantity(diginet_oderbook)
    logger.info('Bitstamp sell price ' + str(bitstamp_sell_price * settings.usd_vnd_rate) +
                ' - Diginet buy price ' + str(diginet_sell_price) +
                ' - Diff: ' + str((bitstamp_sell_price * settings.usd_vnd_rate - diginet_buy_price) / diginet_buy_price) +
                '%')
    logger.info('Diginet sell price ' + str(diginet_sell_price) +
                ' - Bitstamp buy price ' + str(bitstamp_buy_price * settings.usd_vnd_rate) +
                ' - Diff: ' + str((diginet_sell_price / settings.usd_vnd_rate - bitstamp_buy_price) / bitstamp_buy_price) +
                '%')
    if (bitstamp_sell_price * settings.usd_vnd_rate - diginet_buy_price) / diginet_buy_price > settings.diff_pct:
        logger.warning('Buy on diginet -> sell on bitstamp')
    if (diginet_sell_price / settings.usd_vnd_rate - bitstamp_buy_price) / bitstamp_buy_price > settings.diff_pct:
        logger.warning('Buy on bitstamp -> sell on diginet')


def run():
    diginet_orderbook = diginet.fetch_order_book('BTC/VND')
    bitstamp_orderbook = bitstamp.fetch_order_book('BTC/USD')
    compare_prices(bitstamp_orderbook, diginet_orderbook)


if __name__ == '__main__':
    while True:
        try:
            run()
        except Exception as ex:
            logging.error(ex)
        time.sleep(settings.interval)

# b_market = bitstamp.load_markets()
# d_market = diginet.load_markets()
#
# print(d_market)

# d_orderbook = diginet.fetch_order_book('BTC/VND')
#
# print(d_orderbook)
# for ab in d_orderbook:
#     print(d_orderbook[ab])
# d_orderbook = bitstamp.fetch_order_book('BTC/USD')
#
# print(d_orderbook)
# for ab in d_orderbook:
#     print(d_orderbook[ab])

