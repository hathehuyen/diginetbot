from flask import Flask

app = Flask(__name__)

# App config.
DEBUG = True
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '12d441f27d345441f275675d441f2b78617126a'

from frontend import routes
