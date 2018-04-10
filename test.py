from common import db, model
from backend import ordermanager
import configparser
import time

bitstamp_orderbook_btcusd = model.OrderBook(exchange='bitstamp', pair='BTC/USD')
bitstamp_orderbook_btcusd.start()
diginet_orderbook_btcvnd = model.OrderBook(exchange='diginet', pair='BTC/VND')
diginet_orderbook_btcvnd.start()

username = 'huyen'
user_obj = db.UserObj()
user_obj.find_one(username)
# create user if not exist
if not user_obj.id:
    user_obj.username = username
    user_obj.password = '123456'
    user_obj.save()
session_obj = db.SessionObj()
session_obj.find_one(user_id=user_obj.id)
# create session if not exist
if not session_obj.id:
    session_obj.user_id = user_obj.id
    bot_params = configparser.ConfigParser()
    bot_params.read('config.ini')
    session_obj.settings = bot_params
    session_obj.save()

om = ordermanager.OrderManager(bitstamp_orderbook=bitstamp_orderbook_btcusd, diginet_orderbook=diginet_orderbook_btcvnd,
                               session=session_obj)
time.sleep(3)
om.fetch_balance()
