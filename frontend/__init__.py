from flask import Flask, render_template, flash, request, Response
# from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from flask_wtf import Form


# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


@app.route("/", methods=['GET'])
def index():
    return Response('Diginet Bot', mimetype='text/plain')


@app.route("/log", methods=['GET'])
def log():
    with open('diginetbot.log') as f:
        logs = f.read()
    return Response(logs, mimetype='text/plain')


if __name__ == "__main__":
    app.run()
