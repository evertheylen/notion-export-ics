
import traceback
import json
import sys
import os

from flask import Flask

app = Flask(__name__)

with open('settings.json') as f:
    settings = json.load(f)

token = settings['token']

@app.route('/')
def hello():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

