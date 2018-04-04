import ccxt
import settings

diginet = ccxt.acx({'apiKey': '', 'secret': '', 'urls': {'extension': '.json', 'api': 'https://trade.diginet.io'}})
bitstamp = ccxt.bitstamp()

print(settings.bitstamp_oderbook_pct)
# b_market = bitstamp.load_markets()
# d_market = diginet.load_markets()
#
# print(d_market)

# d_orderbook = diginet.fetch_order_book('BTC/VND')
#
# print(d_orderbook)
# for ab in d_orderbook:
#     print(d_orderbook[ab])

