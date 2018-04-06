from frontend import app
from flask import Flask, render_template, flash, request, Response, redirect, url_for
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from frontend.form import LogForm, SettingForm
import configparser


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html', title='Home')


@app.route("/log", methods=['GET'])
def log():
    log_form = LogForm()
    with open('diginetbot.log') as f:
        logs = f.read()
    log_form.log.data = logs
    return render_template('log.html', title='Log', form=log_form)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    # create form
    setting_form = SettingForm()
    # create config object
    bot_params = configparser.ConfigParser()
    if setting_form.validate_on_submit():
        # load config file
        bot_params.read('config.ini')
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
        with open('config.ini', 'w') as configfile:
            bot_params.write(configfile)
        flash('Your changes have been saved.')
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        # load config file
        bot_params.read('config.ini')
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
