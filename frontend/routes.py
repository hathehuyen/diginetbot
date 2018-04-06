from frontend import app
from flask import Flask, render_template, flash, request, Response
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from frontend.form import LogForm, SettingForm
import settings


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


@app.route("/settings", methods=['GET'])
def settings():
    setting_form = SettingForm()
    setting_form.usd_vnd_rate.data = settings.usd_vnd_rate
    setting_form.interval = settings.interval
    return render_template('settings.html', title='Settings', form=setting_form)


if __name__ == "__main__":
    app.run()
