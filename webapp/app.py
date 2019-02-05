
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
    from flup.server.fcgi import WSGIServer
    try:
        WSGIServer(app, bindAddress='./notion-export-ics.sock', umask=0000).run()
    except (KeyboardInterrupt, SystemExit, SystemError):
        print("Shutdown requested... exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)

