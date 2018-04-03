import ccxt

diginet = ccxt.acx({'apiKey': '', 'secret': '', 'urls': {'extension': '.json', 'api': 'https://trade.diginet.io/api'}})

print(diginet.orderbooks)
