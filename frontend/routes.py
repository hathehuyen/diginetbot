from frontend import app
from common import db
import time
from backend import ordermanager
from flask import Flask, render_template, flash, request, Response, redirect, url_for
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from frontend.form import LogForm, SettingForm
import configparser
from common.model import OrderBook

bitstamp_orderbook_btcusd = OrderBook(exchange='bitstamp', pair='BTC/USD')
bitstamp_orderbook_btcusd.start()
diginet_orderbook_btcvnd = OrderBook(exchange='diginet', pair='BTC/VND')
diginet_orderbook_btcvnd.start()
oms = {}


@app.route("/", methods=['GET'])
def index():
    if 'user' not in request.values:
        return render_template('index.html', title='Home')
    username = request.values['username']
    return render_template('index.html', title='Home', username=username)


@app.route("/orderbook", methods=['GET'])
def orderbook():
    if 'ex' not in request.values:
        return Response('Access denied!', content_type='text/plain')
    if request.values['ex'] == 'bitstamp':
        return Response(str(bitstamp_orderbook_btcusd.bids), content_type='text/plain')
    if request.values['ex'] == 'diginet':
        return Response(str(diginet_orderbook_btcvnd.bids), content_type='text/plain')
    return Response('No exchange!', content_type='text/plain')


@app.route("/log", methods=['GET'])
def log():
    if 'user' not in request.values:
        return Response('Access denied!', content_type='text/plain')
    username = request.values['user']
    user_obj = db.UserObj()
    user_obj.find_one(username)
    session_obj = db.SessionObj()
    session_obj.find_one(user_id=user_obj.id)
    log_obj = db.LogObj()
    log_obj.session_id = session_obj.id
    logs = log_obj.get_logs()
    log_lines = []
    log_text = ''
    for line in logs:
        log_lines.insert(0, line)
        if len(log_lines) >= 200:
            break
    for line in log_lines:
        log_text += str(line['text'])
        log_text += '\n'
    log_form = LogForm()
    log_form.log.data = log_text
    return render_template('log.html', title='Log', auto_refresh=True, form=log_form, username=username)


@app.route("/stop", methods=['GET'])
def stop():
    if 'user' not in request.values:
        return redirect(request.host + "/settings")
    global oms
    username = request.values['user']
    if username in oms:
        oms[username].signal = False
        del oms[username]
    return render_template('redirect.html', redirect_url='settings?user=' + username)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if 'user' not in request.values:
        return Response('Access denied!', content_type='text/plain')
    global oms
    username = request.values['user']
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
    # return Response(str(session_obj.settings), content_type='text/plain')

    # create form
    setting_form = SettingForm()
    # create config object
    bot_params = session_obj.settings
    if setting_form.validate_on_submit():
        bot_params['bitstamp']['key'] = setting_form.bitstamp_key.data
        bot_params['bitstamp']['secret'] = setting_form.bitstamp_secret.data
        bot_params['bitstamp']['uid'] = setting_form.bitstamp_uid.data
        bot_params['bitstamp']['orderbook_pct'] = setting_form.bitstamp_orderbook_pct.data
        bot_params['bitstamp']['order_to_copy'] = setting_form.bitstamp_order_to_copy.data
        bot_params['bitstamp']['min_order'] = setting_form.bitstamp_min_order.data
        bot_params['bitstamp']['diff_pct'] = setting_form.bitstamp_diff_pct.data
        bot_params['diginet']['key'] = setting_form.diginet_key.data
        bot_params['diginet']['secret'] = setting_form.diginet_secret.data
        bot_params['diginet']['usd_vnd_rate'] = setting_form.diginet_usd_vnd_rate.data
        bot_params['diginet']['btc_vnd_max'] = setting_form.diginet_btc_vnd_max.data
        bot_params['diginet']['vnd_btc_max'] = setting_form.diginet_vnd_btc_max.data
        bot_params['diginet']['eth_vnd_max'] = setting_form.diginet_eth_vnd_max.data
        bot_params['diginet']['vnd_eth_max'] = setting_form.diginet_vnd_eth_max.data
        bot_params['diginet']['currency_max_pct'] = setting_form.diginet_currency_max_pct.data
        bot_params['diginet']['asset_max_pct'] = setting_form.diginet_asset_max_pct.data
        bot_params['diginet']['min_order'] = setting_form.diginet_min_order.data
        bot_params['bot']['interval'] = setting_form.bot_interval.data

        session_obj.settings = bot_params
        session_obj.save()
        if username not in oms:
            oms[username] = ordermanager.OrderManager(bitstamp_orderbook=bitstamp_orderbook_btcusd,
                                                      diginet_orderbook=diginet_orderbook_btcvnd,
                                                      session=session_obj)
        else:
            oms[username].signal = False
            time.sleep(2)
            oms[username] = ordermanager.OrderManager(bitstamp_orderbook=bitstamp_orderbook_btcusd,
                                                      diginet_orderbook=diginet_orderbook_btcvnd,
                                                      session=session_obj)
        oms[username].run_thread()
        return redirect(request.full_path)
    elif request.method == 'GET':
        setting_form.bitstamp_key.data = bot_params['bitstamp']['key']
        setting_form.bitstamp_secret.data = bot_params['bitstamp']['secret']
        setting_form.bitstamp_uid.data = bot_params['bitstamp']['uid']
        setting_form.bitstamp_orderbook_pct.data = bot_params['bitstamp']['orderbook_pct']
        setting_form.bitstamp_min_order.data = bot_params['bitstamp']['min_order']
        setting_form.bitstamp_order_to_copy.data = bot_params['bitstamp']['order_to_copy']
        setting_form.bitstamp_diff_pct.data = bot_params['bitstamp']['diff_pct']
        setting_form.diginet_key.data = bot_params['diginet']['key']
        setting_form.diginet_secret.data = bot_params['diginet']['secret']
        setting_form.diginet_usd_vnd_rate.data = bot_params['diginet']['usd_vnd_rate']
        setting_form.diginet_btc_vnd_max.data = bot_params['diginet']['btc_vnd_max']
        setting_form.diginet_vnd_btc_max.data = bot_params['diginet']['vnd_btc_max']
        setting_form.diginet_eth_vnd_max.data = bot_params['diginet']['eth_vnd_max']
        setting_form.diginet_vnd_eth_max.data = bot_params['diginet']['vnd_eth_max']
        setting_form.diginet_currency_max_pct.data = bot_params['diginet']['currency_max_pct']
        setting_form.diginet_asset_max_pct.data = bot_params['diginet']['asset_max_pct']
        setting_form.diginet_min_order.data = bot_params['diginet']['min_order']
        setting_form.bot_interval.data = bot_params['bot']['interval']
    bot_status = 'Stopped'
    if username in oms:
        if oms[username].signal:
            bot_status = 'Running'
    return render_template('settings.html', title='Settings', form=setting_form, bot_status=bot_status,
                           username=username)


@app.after_request
def add_header(r):
    """
    Add headers Cache-Control no-cache to browser
    """
    r.headers['Cache-Control'] = 'no-cache'
    return r


if __name__ == "__main__":
    app.run()
