from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LogForm(FlaskForm):
    log = TextAreaField('Log')


class LogInForm(FlaskForm):
    username = TextAreaField('User name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class SettingForm(FlaskForm):
    bot_interval = StringField('Interval')
    bitstamp_key = StringField('Bitstamp key')
    bitstamp_secret = StringField('Bitstamp secret')
    bitstamp_uid = StringField('Bitstamp uid')
    bitstamp_currency_max_pct = StringField('Currency max percent')
    bitstamp_asset_max_pct = StringField('Asset max percent')
    bitstamp_orderbook_pct = StringField('Bitstamp order book percent')
    bitstamp_min_order = StringField('Min order value (usd)')
    bitstamp_order_to_copy = StringField('Number of order to copy')
    bitstamp_diff_pct = StringField('Difference percent')
    diginet_key = StringField('Diginet key')
    diginet_secret = StringField('Diginet secret')
    diginet_usd_vnd_rate = StringField('USD-VND rate')
    diginet_btc_vnd_max = StringField('BTC-VND max')
    diginet_vnd_btc_max = StringField('VND-BTC max')
    diginet_eth_vnd_max = StringField('ETH-VND max')
    diginet_vnd_eth_max = StringField('VND-ETH max')
    diginet_currency_max_pct = StringField('Currency max percent')
    diginet_asset_max_pct = StringField('Asset max percent')
    diginet_min_order = StringField('Min order value (vnd)')
    diginet_diff_pct = StringField('Difference percent')
    submit = SubmitField('Save')
