from frontend import app
from common import db
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


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html', title='Home')


@app.route("/test", methods=['GET'])
def test():
    return Response(str(bitstamp_orderbook_btcusd.bids), content_type='text/plain')


@app.route("/log", methods=['GET'])
def log():
    if 'user' not in request.values:
        return Response('Access denied!', content_type='text/plain')
    log_form = LogForm()
    with open('diginetbot.log') as f:
        logs = f.read()
    log_form.log.data = logs
    return render_template('log.html', title='Log', form=log_form)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if 'user' not in request.values:
        return Response('Access denied!', content_type='text/plain')
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
        # load config file
        # bot_params.read('config.ini')
        # modify config params
        bot_params['bot']['diginet_key'] = setting_form.diginet_key.data
        bot_params['bot']['diginet_secret'] = setting_form.diginet_secret.data
        bot_params['bot']['bitstamp_key'] = setting_form.bitstamp_key.data
        bot_params['bot']['bitstamp_secret'] = setting_form.bitstamp_secret.data
        bot_params['bot']['usd_vnd_rate'] = setting_form.usd_vnd_rate.data
        bot_params['bot']['btc_vnd_max'] = setting_form.btc_vnd_max.data
        bot_params['bot']['vnd_btc_max'] = setting_form.vnd_btc_max.data
        bot_params['bot']['eth_vnd_max'] = setting_form.eth_vnd_max.data
        bot_params['bot']['vnd_eth_max'] = setting_form.vnd_eth_max.data
        bot_params['bot']['currency_max_pct'] = setting_form.currency_max_pct.data
        bot_params['bot']['asset_max_pct'] = setting_form.asset_max_pct.data
        bot_params['bot']['bitstamp_oderbook_pct'] = setting_form.bitstamp_oderbook_pct.data
        bot_params['bot']['bitstamp_min_order'] = setting_form.bitstamp_min_order.data
        bot_params['bot']['diff_pct'] = setting_form.diff_pct.data
        bot_params['bot']['interval'] = setting_form.interval.data
        # save config file
        # with open('config.ini', 'w') as configfile:
        #     bot_params.write(configfile)
        # flash('Your changes have been saved.')
        # return redirect(url_for('settings'))
        # save config to db
        session_obj.settings = bot_params
        session_obj.save()
        return redirect(request.full_path)
    elif request.method == 'GET':
        setting_form.diginet_key.data = bot_params['bot']['diginet_key']
        setting_form.diginet_secret.data = bot_params['bot']['diginet_secret']
        setting_form.bitstamp_key.data = bot_params['bot']['bitstamp_key']
        setting_form.bitstamp_secret.data = bot_params['bot']['bitstamp_secret']
        setting_form.usd_vnd_rate.data = bot_params['bot']['usd_vnd_rate']
        setting_form.btc_vnd_max.data = bot_params['bot']['btc_vnd_max']
        setting_form.vnd_btc_max.data = bot_params['bot']['vnd_btc_max']
        setting_form.eth_vnd_max.data = bot_params['bot']['eth_vnd_max']
        setting_form.vnd_eth_max.data = bot_params['bot']['vnd_eth_max']
        setting_form.currency_max_pct.data = bot_params['bot']['currency_max_pct']
        setting_form.asset_max_pct.data = bot_params['bot']['asset_max_pct']
        setting_form.bitstamp_oderbook_pct.data = bot_params['bot']['bitstamp_oderbook_pct']
        setting_form.bitstamp_min_order.data = bot_params['bot']['bitstamp_min_order']
        setting_form.diff_pct.data = bot_params['bot']['diff_pct']
        setting_form.interval.data = bot_params['bot']['interval']
    return render_template('settings.html', title='Settings', form=setting_form)


if __name__ == "__main__":
    app.run()
