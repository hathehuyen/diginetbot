from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LogForm(FlaskForm):
    log = TextAreaField('Log')


class SettingForm(FlaskForm):
    diginet_key = StringField('Diginet key')
    diginet_secret = StringField('Diginet secret')
    bitstamp_key = StringField('Bitstamp key')
    bitstamp_secret = StringField('Bitstamp secret')
    usd_vnd_rate = StringField('USD-VND rate')
    btc_vnd_max = StringField('BTC-VND max')
    vnd_btc_max = StringField('VND-BTC max')
    eth_vnd_max = StringField('ETH-VND max')
    vnd_eth_max = StringField('VND-ETH max')
    currency_max_pct = StringField('Currency max percent')
    asset_max_pct = StringField('Asset max percent')
    bitstamp_oderbook_pct = StringField('Bitstamp order book percent')
    bitstamp_min_order = StringField('Bitstamp min order')
    diff_pct = StringField('Difference percent')
    interval = StringField('Interval')

